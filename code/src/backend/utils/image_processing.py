import concurrent.futures
from utils.download_image import download_image
from data_extraction.ocr import extract_text_from_image
from models.blip import generate_caption
from models.llama import summarize_text
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Load environment variables
CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
ATLASSIAN_AUTH = (os.getenv("CONFLUENCE_USER"), os.getenv("CONFLUENCE_API_TOKEN"))

def process_image(elem, page_id):
    """
    Process an image element by downloading it, running OCR and BLIP, 
    and summarizing the combined results.

    Args:
        elem: BeautifulSoup element containing the image.
        page_id: The Confluence page ID for fetching attachments.

    Returns:
        str: Summarized text from the image (OCR + BLIP).
    """
    try:
        # Get the image URL
        image_url = get_image_url(elem, page_id)
        if not image_url:
            return "No image URL found."
        return process_image_from_url(image_url)
    except Exception as e:
         print(f"Error processing image: {str(e)}")

def process_image_from_url(image_url):
    try:
        # Download the image
        image = download_image(image_url)
        if not image:
            return "Failed to download image."

        # Process OCR and BLIP simultaneously
        with concurrent.futures.ThreadPoolExecutor() as executor:
            ocr_future = executor.submit(extract_text_from_image, image)
            caption_future = executor.submit(generate_caption, image)

            ocr_text = ocr_future.result()
            caption = caption_future.result()
        
        # Summarize the combined result using LLaMA
        summary = summarize_text(get_prompt(ocr_text, caption))
        return summary

    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return "Error: Image processing failed."
    
def get_prompt(ocr_text, caption):
    return f"'''{ocr_text}''' This is the text we have from the OCR and '''{caption}''' is the summary of what is present in the image. Get a detailed summary of what is present in the image. Don't miss any details present in the image"

def get_image_url(elem, page_id):
    """
    Fetch the image URL from the 'ac:image' tag.
    """
    attachment_tag = elem.find('ri:attachment')
    if not attachment_tag:
        print("No attachment found within the image tag.")
        return None

    file_name = attachment_tag.get('ri:filename')

    # API endpoint to get attachments
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}/child/attachment"

    # Fetch attachment data
    response = requests.get(url, auth=ATLASSIAN_AUTH)
    if response.status_code != 200:
        print(f"Failed to fetch attachment details. Status code: {response.status_code}")
        return None

    data = response.json()

    # Extract the download URL from the response
    for attachment in data.get("results", []):
        if attachment.get("title") == file_name:
            image_url = attachment.get("_links", {}).get("download")
            if image_url:
                full_image_url = f"{CONFLUENCE_BASE_URL}{image_url}"
                print(f"Image URL found: {full_image_url}")
                return full_image_url

    print("Image URL not found.")
    return None
