from PIL import Image
# import requests
import os
from io import BytesIO
from dotenv import load_dotenv
from huggingface_hub import InferenceClient, InferenceApi

# # Load environment variables
load_dotenv()
# # Load environment variables
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_API_URL = os.getenv("HUGGINGFACE_API_URL")
BLIP_MODEL_NAME = os.getenv("BLIP_MODEL_NAME")

def generate_caption(image: Image.Image) -> str:
    """
    Generates a caption for the given PIL Image object using the BLIP model.

    Args:
        image (Image.Image): The image object.

    Returns:
        str: Generated caption.
    """
    try:
        # headers = {
        #     "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        #     "Content-Type": "application/octet-stream"
        # }

        api_url = f"{HUGGINGFACE_API_URL}/{BLIP_MODEL_NAME}"
        image_byte_array = BytesIO()
        image.save(image_byte_array, format="JPEG")  # Convert to bytes
        image_byte_array.seek(0)

        print("Sending API request")

        # response = requests.post(api_url, headers=headers, data=image_byte_array.getvalue())
        # response.raise_for_status()
        # result = response.json()

        client = InferenceClient(
            token=HUGGINGFACE_API_KEY,
            model="Salesforce/blip-image-captioning-large"
        )
        result = client.image_to_text(
            image=image_byte_array.getvalue(),
            model="Salesforce/blip-image-captioning-large"
        )

        # result = inference(data=image_byte_array.getvalue(), is_binary=True)

        caption = result.get("generated_text")
        print(caption)

        return caption

    except Exception as e:
        print(f"Error generating caption: {str(e)}")
        return "Error: Could not generate caption."





