from dotenv import load_dotenv
import chromadb 
import os 

load_dotenv()

#Loaded the env variables
dbHost=os.getenv("DB_HOST")
dbPort=os.getenv("DB_PORT")

chromaClient=chromadb.HttpClient(host=dbHost,port=dbPort)
collections = chromaClient.list_collections()

chromaClient.delete_collection(name="golang_docs")

print("All collections deleted.")


