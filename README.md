# Go Documentation AI Assistant 🚀  

This project is an AI-powered assistant that retrieves and answers questions based on Golang documentation using **ChromaDB**, **Ollama LLM**, and **LangChain**.  

## Features  
✅ Retrieves relevant Golang documentation from **ChromaDB**  
✅ Uses **DeepSeek-R1 1.5B** LLM for answering questions  
✅ Embeds queries using **bge-large** model  
✅ Supports **streaming responses** for better user experience  
✅ Implements **self-check mechanism** to avoid hallucinations  

---

## 🛠️ Setup Instructions  

### 1 Prerequisites  
Ensure you have the following installed:  
- Python 3.8+  
- Docker (for ChromaDB)  
- Ollama (for LLM inference)  


### 2 Environment variables  
```bash
export TARGET_WEBSITE="https://pkg.go.dev"
export DB_HOST="localhost"
export DB_PORT=8000"


### 3 Clone the Repository  
```bash
git clone https://github.com/your-repo/go-doc-ai.git
cd go-doc-ai



