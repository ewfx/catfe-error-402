import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load environment variables
CHATGROQ_API_KEY = os.getenv("CHATGROQ_API_KEY")
CHATGROQ_API_URL = os.getenv("CHATGROQ_API_URL")
LLAMA_MODEL_NAME = os.getenv("LLAMA_MODEL_NAME")

SYSTEM_MESSAGE = """
    You are a highly efficient assistant designed to generate accurate and concise summaries of text extracted from images and their captions. Your primary goal is to combine the extracted text and caption in a coherent and meaningful way, while retaining key information and maintaining clarity.
"""

def summarize_text(prompt: str, system_message: str = SYSTEM_MESSAGE) -> str:
    """
    Calls the ChatGroq API to generate a summary using the LLama model.

    Args:
        prompt (str): The input text to be summarized.
        system_message (str): The system instruction message for LLama.

    Returns:
        str: The summarized output from LLama.
    """
    try:
        headers = {
            "Authorization": f"Bearer {CHATGROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": LLAMA_MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "max_completion_tokens": 700,
            "temperature": 0.0,
            "top_p": 1.0,
            "n": 1,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0,
            "seed": 47,
            "stream": False

        }

        response = requests.post(CHATGROQ_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        # Extract and return the generated text
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return "No response generated."

    except Exception as e:
        print(f"Error during LLama summarization: {str(e)}")
        return "Error: Could not generate summary."
