import os
import requests
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Load environment variables
CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
CONFLUENCE_USER = os.getenv("CONFLUENCE_USER")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_AUTH = (CONFLUENCE_USER, CONFLUENCE_API_TOKEN)

def download_image(image_url: str) -> Image.Image:
    """
    Downloads an image from a given URL and returns it as a PIL Image object.

    Args:
        image_url (str): URL of the image to download.

    Returns:
        Image.Image: PIL Image object.
    """
    try:
        headers = {
            "Authorization": f"Basic {os.getenv('CONFLUENCE_USER')}:{os.getenv('CONFLUENCE_API_TOKEN')}"
        }

        # Request the image
        response = requests.get(image_url, auth=CONFLUENCE_AUTH, headers=headers)
        response.raise_for_status()

        # Load the image from bytes
        image = Image.open(BytesIO(response.content)).convert('RGB')
        return image

    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return None
