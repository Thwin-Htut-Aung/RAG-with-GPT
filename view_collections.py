import chromadb
import os

# Initialize the client
persist_directory = os.path.abspath("data")
client = chromadb.PersistentClient(path=persist_directory)


collection = client.get_collection("pdf_embeddings")
print(f"Collection count: {collection.count()}")