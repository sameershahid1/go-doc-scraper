from langchain.text_splitter import RecursiveCharacterTextSplitter
# import google.generativeai as genai
from urllib.parse import urljoin
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from tabulate import tabulate
import requests
import chromadb
import ollama
import asyncio
import time
import os
import re


# ✂️ Function to Chunk Text Properly
def splitTextLangchain(text, chunk_size=200, overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(text)


def getGeminiEmbedding(text):
    # model = "models/embedding-001"
    # response = genai.embed_content(
    #    model=model, content=text, task_type="RETRIEVAL_DOCUMENT")
    response = ollama.embeddings(model="bge-large:latest", prompt=text)

    return response["embedding"]


def getAllGolangPackages(BASE_URL, path):
    """Scrapes third-party Go packages from /search?q="""
    url = f"{BASE_URL}/{path}"
    package_links = []
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ Error fetching third-party packages from {url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract package links
    links = [
        urljoin(BASE_URL, a["href"])
        for a in soup.select("a[href^='/']")  # Find all internal links
    ]

    package_links.extend(links)

    time.sleep(1)  # Avoid hitting rate limits

    return list(set(package_links))  # Remove duplicates


def sanitize_filename(url):
    """ Convert a URL into a safe filename by removing invalid characters. """
    filename = re.sub(r'[^\w\-_\.]', '_',
                      url)  # Replace special characters with '_'
    return filename[:100]  # Limit filename length


def cleanContent(text):
    """Cleans extracted text while preserving code blocks properly."""

    text = text.strip()
    code_blocks = re.findall(r"```(.*?)```", text, re.DOTALL)
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(\n\s*){2,}', '\n', text)
    text = re.sub(r'(?<!`)`{1,3}(?!`)', '', text)
    text = re.sub(r'[*_~]', '', text)

    for block in code_blocks:
        text = text.replace(block.strip(), f"```{block.strip()}```")

    return text.strip()  # Final clean trim


def scrapeGolangDocs(url, save_dir="scraped_docs"):
    """Scrapes Golang documentation, extracts structured content, and saves it.
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Error fetching {url}: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    extracted_text = []

    # 📝 Extract headings, paragraphs, and list items
    for tag in ["h1", "h2", "h3", "h4", "p", "li"]:
        for element in soup.find_all(tag):
            extracted_text.append(element.get_text(strip=True))

    # 🖥️ Extract properly formatted code blocks
    for pre in soup.find_all("pre"):
        # Avoid duplicate `<code>` inside `<pre>`
        if pre.find("code"):
            code_text = pre.find("code").get_text()
        else:
            code_text = pre.get_text()
        extracted_text.append(f"```go\n{code_text.strip()}\n```")

    # 🔹 Extract inline code snippets inside paragraphs
    for code in soup.find_all("code"):
        inline_code = code.get_text(strip=True)
        if inline_code and f"`{inline_code}`" not in extracted_text:  # Avoid duplication
            extracted_text.append(f"`{inline_code}`")

    # 📊 Extract and format tables safely
    for table in soup.find_all("table"):
        rows = []
        for row in table.find_all("tr"):
            columns = [col.get_text(strip=True)
                       for col in row.find_all(["td", "th"])]
            if columns:
                rows.append(columns)
        if rows:
            table_text = tabulate(rows, tablefmt="grid")
            extracted_text.append(f"\n{table_text}\n")

    # 💡 Extract blockquotes & asides properly
    for aside in soup.find_all(["aside", "blockquote"]):
        aside_text = aside.get_text().strip().replace("\n", " ")
        extracted_text.append(f"💡 {aside_text}")

    # 📄 Convert extracted text into a single cleaned string
    full_text = cleanContent("\n\n".join(extracted_text))

    # 🔹 Ensure save directory exists
    os.makedirs(save_dir, exist_ok=True)

    # 🔹 Generate a safe filename
    filename = sanitize_filename(url) + ".txt"
    file_path = os.path.join(save_dir, filename)

    # 🔹 Save the extracted text to a file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(full_text)

    print(f"✅ Saved: {file_path}")
    return full_text


def scrapeAndStore(collection, targetWebsie, path):
    packageUrls = getAllGolangPackages(targetWebsie, path)

    for pkgUrl in packageUrls:
        textContent = scrapeGolangDocs(pkgUrl)

        if textContent:
            chunks = splitTextLangchain(textContent)
            for i, chunk in enumerate(chunks):
                embedding = getGeminiEmbedding(chunk)
                ids = f"{pkgUrl}#chunk-{i}"
                metaData = {
                    "url": pkgUrl,
                    "chunk": i,
                    "totalChunk": len(chunks)
                }

                collection.add(
                    ids=[ids],
                    embeddings=[embedding],
                    metadatas=[metaData],
                    documents=[chunk],
                )

        else:
            print(f"⚠️ Skipped {pkgUrl} due to an error.")

        time.sleep(1)  # Rest for server
        print("🎉 Scraping complete!")


async def main():
    load_dotenv()
    # llmApiKey = os.getenv("GEMINI_API_KEY")
    dbHost = os.getenv("DB_HOST")
    dbPort = os.getenv("DB_PORT")
    targetWebSite = os.getenv("TARGET_WEBSITE")

    if not dbPort and not dbHost:
        return

    # genai.configure(api_key=llmApiKey)
    chromaClient = chromadb.HttpClient(host=dbHost, port=dbPort)
    collection = chromaClient.get_or_create_collection(name="golang_docs")

    thirdPartyPath = "search?q=golang.org"
    standardPath = "std"
    # basicConcepts = "https://go.dev/doc/"

    # print("Starting basic concepts docs")
    # scrapeAndStore(collection, basicConcepts, "")

    print("Starting-Third party package extraction")
    scrapeAndStore(collection, targetWebSite, thirdPartyPath)

    print("Starting-Standard package extraction")
    scrapeAndStore(collection, targetWebSite, standardPath)


if __name__ == "__main__":
    asyncio.run(main())
