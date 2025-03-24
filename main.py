from fastapi import FastAPI, HTTPException
from langchain_google_genai import GoogleGenerativeAI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain_chroma import Chroma
from dotenv import load_dotenv
from pydantic import BaseModel
import chromadb
import asyncio
import ollama
import os

import logging

load_dotenv()
app = FastAPI()

logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatQuery(BaseModel):
    query: str
    model: str


def getLLM(model: str):
    match model:
        case "deepseek-r1:1.5b":
            return OllamaLLM(
                model="deepseek-r1:1.5b",
                temperature=0.1,
                num_ctx=8500,
                top_p=0.9,
                top_k=40,
            )
        case "gemini":
            gemini = GoogleGenerativeAI(
                model="gemini-2.0-flash-thinking-exp-01-21",
                google_api_key="AIzaSyCEL1gMB3WhZVXPjtFOedl-DT_X0OIv0xI",
                max_output_tokens=8500,
                temperature=0.7,
                streaming=True,
                top_p=0.9,
                top_k=80,
            )

            return gemini

    return None


def getQueryEmbedding(prompt: str):
    response = ollama.embeddings(
        model="qllama/bge-small-en-v1.5:latest", prompt=prompt)
    return response["embedding"]


async def retrieveContexts(vectorstore, varitionQuery):
    allDocsAsync = []
    allDocs = []
    for query in varitionQuery:
        embedding = getQueryEmbedding(query)
        docsAsync = vectorstore.asimilarity_search_by_vector(embedding, k=30)
        allDocsAsync.append(docsAsync)

    results = await asyncio.gather(*allDocsAsync)
    for result in results:
        if not result:
            continue
        allDocs.extend(result)

    context = "\n\n".join(set([doc.page_content for doc in allDocs]))
    return context


def getChromaDb(dbHost: str, dbPort: int):
    chromaClient = chromadb.HttpClient(host=dbHost, port=dbPort)
    vectorstore = Chroma(
        collection_name="golang_docs",
        client=chromaClient,
    )

    return vectorstore


def expandQuery(query: str, model: str):
    prompt = f"""
    Generate **5 diverse variations** of the following query to help retrieve relevant Golang documentation.
    The variations should rephrase the question in **different ways** to improve search results.

    **Original Query:** "{query}"

    **Examples of Good Variations:**
    - "What does '{query}' mean in Golang?"
    - "Explain '{query}' with examples."
    - "How does '{query}' work in Golang?"

    **Return variations as a numbered list.**
    """
    llm = getLLM(model)
    if not llm:
        return None
    response = llm.invoke(prompt)
    variations = [line.strip("12345.- ")
                  for line in response.split("\n") if line.strip()]
    variations = variations[1:]
    return variations


async def getGeminiStream(llm, formatedPrompt: str):
    response = llm.astream(formatedPrompt)
    async for chunk in response:
        yield chunk
        await asyncio.sleep(0)


async def getOllamaStream(llm, formatPrompt: str):
    for token in llm.stream(formatPrompt):
        yield token
        await asyncio.sleep(0)


async def llmWorkflow(chat: ChatQuery):
    dbHost = os.getenv("DB_HOST")
    dbPort = os.getenv("DB_PORT")
    if not dbHost or not dbPort:
        return None

    queryVariation = expandQuery(chat.query, chat.model)
    if not queryVariation:
        return None
    vectorStore = getChromaDb(dbHost, int(dbPort))
    context = await retrieveContexts(vectorStore, queryVariation)
    promptTemplate = PromptTemplate(
        input_variables=["query", "context"],
        template="""
        You are an AI assistant specializing in **Golang documentation**.
        You are **not a general AI**, **not a chatbot**, and you should never claim
        to be anything other than a **Golang documentation assistant**.

        ### **Rules for Responses:**
        - Always **think before responding**, ensuring accuracy.
        - Do **not generate any information** beyond what is provided in the context.
        - If the user asks about your identity, always respond with:
            **"I am a Golang documentation assistant, nothing more."**
        - If the answer is not found in the provided documentation, respond with:
        **"Not enough documentation found."**
        ---

        ### **Context:**
        {context}

        ### **User Question:**
        "{query}"

        ### **Response (strictly based on context):**
        [Provide the response strictly from the context]
    """
    )

    formatPrompt = promptTemplate.format(query=chat.query, context=context)
    llm = getLLM(chat.model)
    if not llm:
        return None

    match chat.model:
        case "gemini":
            return StreamingResponse(
                getGeminiStream(llm, formatPrompt),
                media_type="text/plain",
            )
        case "deepseek-r1:1.5b":
            return StreamingResponse(
                getOllamaStream(llm, formatPrompt),
                media_type="text/plain")

    return None


@app.post("/chat/query")
async def user_query(chat: ChatQuery):
    try:
        stream = await llmWorkflow(chat)
        if not stream:
            logger.error("llmWorkflow returned None")
            raise HTTPException(
                status_code=500, detail="LLM workflow failed to produce a stream.")
        return stream
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        logger.exception("Error in llmWorkflow")
        raise HTTPException(
            status_code=500, detail="Internal server error during LLM workflow.")
