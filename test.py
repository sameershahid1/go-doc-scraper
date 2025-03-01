from dotenv import load_dotenv
import chromadb
import ollama
import re
import os
import sys


def cleanContent(text):
    """Cleans extracted text while preserving code blocks properly."""
    text = text.strip()
    code_blocks = re.findall(r"```(.*?)```", text, re.DOTALL)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(\n\s*){2,}', '\n', text)
    text = re.sub(r'(?<!`)`{1,3}(?!`)', '', text)
    text = re.sub(r'[*_~]', '', text)
    for block in code_blocks:
        text = text.replace(block.strip(), f"```{block.strip()}```")

    return text


def getQueryEmbedding(text):
    response = ollama.embeddings(model="bge-large:latest", prompt=text)
    return response["embedding"]


# Loaded the env variables
load_dotenv()

dbHost = os.getenv("DB_HOST")
dbPort = os.getenv("DB_PORT")
chromaClient = chromadb.HttpClient(host=dbHost, port=dbPort)
collection = chromaClient.get_or_create_collection(name="golang_docs")

query_text = cleanContent(
    """what is cmd in golang""")

query_embedding = getQueryEmbedding(query_text)

# Estimate memory usage (for all embeddings & metadata)
size = sum(sys.getsizeof(doc) for doc in collection.get()["documents"])
print(f"Estimated memory usage: {size / (1024*1024):.2f} MB")

print(collection.count())

results = collection.query(
    query_embeddings=[query_embedding],
)

print("🔎 Similar Docs:", results["documents"])
