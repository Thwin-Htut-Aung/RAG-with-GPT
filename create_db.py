import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

api_key = os.environ['OPENAI_API_KEY']

# Function to read PDF and extract text
def extract_data_from_file(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Function to split text into chunks
def split_data(data):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=215,
        chunk_overlap= 60,
        length_function=len
    )
    chunks = text_splitter.split_text(data)
    print("The text is split into " + str(len(chunks)) + " chunks")
    return chunks

# Function to generate embeddings
def generate_embeddings(chunks):
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    return [embeddings.embed_query(chunk) for chunk in chunks]

def store_in_db(chunks, embeddings):
    persist_directory = os.path.abspath("data")
    print(f"Using directory: {persist_directory}")

    client = chromadb.PersistentClient(path=persist_directory)
    
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=api_key,
                model_name="text-embedding-ada-002"
            )
    
    collection = client.get_or_create_collection(
        name="product_embeddings",
        embedding_function=openai_ef
    )
    
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        print(f"Storing Chunk {i}")
        collection.add(
            embeddings=[embedding],
            documents=[chunk],
            ids=[f"chunk_{i}"]
        )
    
    print(f"Total items in collection: {collection.count()}")
    
    # Check directory contents
    print("Directory contents:")
    for root, dirs, files in os.walk(persist_directory):
        level = root.replace(persist_directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")


# Main function
def process_pdf(pdf_path):
    # Extract text from PDF
    data = extract_data_from_file(pdf_path)
    
    # Split text into chunks
    print("Getting Chunks")
    chunks = split_data(data)
    
    print("Generating Embeddings")
    # Generate embeddings
    embeddings = generate_embeddings(chunks)
    
    print("Storing chunks and embeddings")
    # Store in ChromaDB
    store_in_db(chunks, embeddings)

# Usage
pdf_path = "products_dataset.pdf"
process_pdf(pdf_path)
