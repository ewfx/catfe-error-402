import os
import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from sentence_transformers import SentenceTransformer

# # Load environment variables
load_dotenv()
# Load environment variables
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_API_URL = os.getenv("HUGGINGFACE_API_URL")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

def generate_embeddings(text_chunks: list) -> list:
    """
    Generate embeddings for a list of text chunks in a batch.

    Args:
        text_chunks (list): A list of text chunks to generate embeddings for.

    Returns:
        list: A list of embedding vectors.
    """
    try:
        # headers = {
        #     "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        #     "Content-Type": "application/json"
        # }

        # api_url = f"{HUGGINGFACE_API_URL}/{EMBEDDING_MODEL_NAME}/embeddings"
        # data = {
        #     "inputs": text_chunks
        # }

        # response = requests.post(api_url, headers=headers, json=data)
        # response.raise_for_status()
        # result = response.json()

        # Extract embeddings from the response
        # embeddings = [item["embedding"] for item in result]

        return embedding_model.encode(text_chunks, convert_to_numpy=True, batch_size=8)

    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        return []
