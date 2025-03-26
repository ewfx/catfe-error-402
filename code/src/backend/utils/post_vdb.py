from pinecone import Pinecone, ServerlessSpec
import time
import numpy as np
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Initialize Pinecone with API key
pc = Pinecone(api_key=PINECONE_API_KEY)
def post_embeddings(embeddings, metadata):
    # Create an index if it doesn’t exist
    embeddings = np.array(embeddings)
    index_name = "fraud-detection-file"
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=768,  # Use 768 for all-mpnet-base-v2 embeddings
            metric="cosine",  # Best for NLP tasks
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

    # Connect to the existing index
    index = pc.Index(index_name)
    print(f"Connected to Pinecone index: {index_name}")

    # Store embeddings along with metadata (text content)
    try:
        for i, emb in enumerate(embeddings):
            # metadata = {"text": final_text[i][1], "title": final_text[i][0]}  # Associate text with each vector
            index.upsert([(str(i), emb.tolist(), metadata[i])])
            # index.upsert([(str(i), emb.tolist(), metadata)])
    except Exception as e:
        print(e)

#    text, timstamp, 