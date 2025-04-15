from pymongo import MongoClient
from urllib.parse import quote_plus

username = quote_plus("sid")
password = quote_plus("sinDMong0Db@2024")  

MONGO_URI = f"mongodb://{username}:{password}@10.60.1.10:27017"
DB_NAME = "chatbot_ollama_service"
COLLECTION_NAME = "pdf_cache"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
pdf_cache_collection = db[COLLECTION_NAME]
