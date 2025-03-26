import os
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Pinecone
def init_pinecone():
    api_key = os.getenv("pineconeAPIKey")
    index_name = os.getenv("INDEX_NAME")
    print(api_key)

    # Connect to Pinecone
    pc = Pinecone(api_key=api_key)

    # Create the index if it doesn't exist
    if index_name not in pc.list_indexes().names():
        print(f"Creating index '{index_name}'...")
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

    # Connect to the index
    index = pc.Index(index_name)
    print(f"✅ Connected to Pinecone index: {index_name}")
    
    return index


def get_vector_store():
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    index=init_pinecone()
    # ✅ Correct integration using PineconeVectorStore
    vector_store = PineconeVectorStore(index, embedding_model)
    return vector_store