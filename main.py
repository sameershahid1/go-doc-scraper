from langchain.callbacks.base import BaseCallbackHandler
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain_chroma import Chroma
from dotenv import load_dotenv
import chromadb
import asyncio
import ollama
import os


class StreamingCallbackHandler(BaseCallbackHandler):
    """Custom callback handler to handle streaming output."""

    def __init__(self):
        self.response = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.response += token
        print(token, end="", flush=True)

    def get_response(self):
        return self.response


def getLLM():
    llm = OllamaLLM(
        callbacks=[StreamingCallbackHandler()],
        model="deepseek-r1:1.5b",
        temperature=0.1,
        num_ctx=2500,
        top_p=0.9,
        top_k=40,
    )

    return llm


def getQueryEmbedding(prompt: str):
    response = ollama.embeddings(model="bge-large:latest", prompt=prompt)
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


def getChromaDb(dbHost, dbPort):
    chromaClient = chromadb.HttpClient(host=dbHost, port=dbPort)
    vectorstore = Chroma(
        collection_name="golang_docs",
        client=chromaClient,
    )

    return vectorstore


def expandQuery(query):
    variations = [
        query,
        f"What does '{query}' mean in Golang?",
        f"Explain '{query}' with examples.",
        f"How does '{query}' work in Golang?",
    ]
    return variations


# 🏁 Run the whole process
async def main():
    load_dotenv()
    dbHost = os.getenv("DB_HOST")
    dbPort = os.getenv("DB_PORT")

    query = """What are the security step of golang."""
    queryVariation = expandQuery(query)
    vectorStore = getChromaDb(dbHost, dbPort)
    context = await retrieveContexts(vectorStore, queryVariation)
    promptTemplate = PromptTemplate(
        input_variables=["query", "context"],
        template="""
        You are an AI assistant specializing in Golang documentation.
        Your responses **must be strictly based on the provided documentation**.

        If you are unsure, reply with:
        **"Not enough documentation found."**

        **Context:**
        {context}

        **User Question:**
        "{query}"

        **Response (strictly based on context, don't create think your self,
                     just use the provided document for the reference):**
    """
    )

    formatPrompt = promptTemplate.format(query=query, context=context)
    llm = getLLM()
    llm.invoke(formatPrompt)

if __name__ == "__main__":
    asyncio.run(main())
