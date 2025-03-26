from PIL import Image
import pytesseract

def extract_text_from_image(image: Image.Image) -> str:
    """
    Extracts text from a given PIL Image object using Tesseract OCR.

    Args:
        image (Image.Image): The image object.

    Returns:
        str: Extracted text.
    """
    try:
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"Error during OCR processing: {str(e)}")
        return "Error: Could not extract text from image."
