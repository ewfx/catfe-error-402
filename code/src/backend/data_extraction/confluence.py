import os
from atlassian import Confluence
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
CONFLUENCE_USER = os.getenv("CONFLUENCE_USER")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

# Initialize Confluence client
confluence = Confluence(
    url=CONFLUENCE_BASE_URL,
    username=CONFLUENCE_USER,
    password=CONFLUENCE_API_TOKEN
)

def get_all_confluence_urls(url: str):
    """
    Recursively fetches all Confluence page URLs from the given URL, including nested pages and spaces.

    Args:
        url (str): The root Confluence URL.

    Returns:
        list: A list of unique Confluence page URLs.
    """
    visited_urls = set()
    page_urls = set()

    def fetch_space_urls(space_key):
        """
        Fetch all pages from a given space key.
        """
        try:
            start = 0
            limit = 50
            while True:
                # Fetch pages from the space
                pages = confluence.get_all_pages_from_space(
                    space=space_key, start=start, limit=limit, expand="title"
                )
                # print(pages)
                if not pages:
                    break

                # Extract URLs of pages in the space
                for page in pages:
                    page_id = page.get("id")
                    title = page.get("title")
                    webui_link = page.get("_links", {}).get("webui")
                    if page_id and title and webui_link:
                        page_url = f"{CONFLUENCE_BASE_URL}{webui_link}"
                        if page_url not in page_urls:
                            page_urls.add(page_url)

                start += limit

        except Exception as e:
            print(f"Error fetching pages from space '{space_key}': {str(e)}")

    def fetch_child_urls(current_url):
        """
        Recursively fetch child pages from a given page URL.
        """
        nonlocal visited_urls, page_urls

        # Prevent duplicate visits
        if current_url in visited_urls:
            return []

        visited_urls.add(current_url)

        # Get page ID from the URL
        page_id = extract_page_id(current_url)
        if not page_id:
            return []

        # Include the current page URL itself
        if is_page_or_folder(current_url) == "page" and current_url not in page_urls:
            page_urls.add(current_url)

        try:
            # Fetch child pages using the Confluence API
            children = confluence.get_page_child_by_type(page_id=page_id, type="page", start=0, limit=50)

            # Extract URLs of child pages
            for page in children:
                child_id = page.get("id")
                title = page.get("title")
                webui_link = page.get("_links", {}).get("webui")
                if child_id and title and webui_link:
                    # Construct the full page URL using the webui link
                    child_url = f"{CONFLUENCE_BASE_URL}{webui_link}"
                    if child_url not in page_urls:
                        page_urls.add(child_url)
                        # Recursively fetch nested child pages
                        fetch_child_urls(child_url)

        except Exception as e:
            print(f"Error fetching child pages: {str(e)}")


    # Determine if the given URL is a space URL or a page URL
    page_id = extract_page_id(url)
    space_key = extract_space_key(url)

    if page_id:
        fetch_child_urls(url)
    elif space_key:
        fetch_space_urls(space_key)

    # Convert set to list and return
    return list(page_urls)

def extract_page_id(url: str) -> str:
    """
    Extracts the page ID from a Confluence URL, handling various formats.

    Args:
        url (str): The Confluence page or folder URL.

    Returns:
        str: Page ID extracted from the URL.
    """
    try:
        # Split the URL to remove query parameters
        base_url = url.split('?')[0]
        parts = base_url.split('/')

        # Search for a numeric ID in the URL parts
        for part in parts:
            if part.isdigit():
                return part

        print(f"Unable to extract page ID from URL: {url}")
        return None
    except Exception as e:
        print(f"Error extracting page ID: {str(e)}")
        return None

def extract_space_key(url: str) -> str:
    """
    Extracts the space key from a Confluence space URL.

    Args:
        url (str): The Confluence space URL.

    Returns:
        str: Space key extracted from the URL.
    """
    try:
        parts = url.split('/')
        # Find the space key after "spaces"
        if "spaces" in parts:
            space_index = parts.index("spaces") + 1
            space_key = parts[space_index]
            if space_key.startswith("~"):
                return space_key  # User-specific space
            return space_key
        return None
    except Exception as e:
        print(f"Error extracting space key from URL: {str(e)}")
        return None

def is_page_or_folder(url: str) -> str:
    """
    Determines whether the given URL is a Confluence page or a folder.

    Args:
        url (str): The Confluence URL to check.

    Returns:
        str: "page" if it is a page URL, "folder" if it is a folder URL, "unknown" otherwise.
    """
    # Try to detect based on URL pattern
    if "/folder/" in url:
        return "folder"
    elif "/pages/" in url:
        return "page"

def get_all_confluence_data(url: str):
    """
    Fetches detailed data (soup, page_id, space_key) for all pages returned by get_all_confluence_urls.

    Args:
        url (str): The root Confluence URL.

    Returns:
        list: A list of dictionaries containing page URL, soup, page ID, and space key.
    """
    page_urls = get_all_confluence_urls(url)
    page_data = []

    for page_url in page_urls:
        page_id = extract_page_id(page_url)
        space_key = extract_space_key(page_url)
        soup = get_page_soup(page_id)
        if soup:
            page_data.append({
                "url": page_url,
                "soup": soup,
                "page_id": page_id,
                "space_key": space_key
            })

    return page_data

def get_page_soup(page_id: str):
    """
    Fetches the page content as a BeautifulSoup object.

    Args:
        page_id (str): The page ID.

    Returns:
        BeautifulSoup: Parsed page content.
    """
    try:
        content = confluence.get_page_by_id(page_id, expand="body.storage")
        if content:
            page_html = content.get("body", {}).get("storage", {}).get("value", "")
            page_html = f"<h1>{content.get("title", "")}</h1>\n" + page_html
            return BeautifulSoup(page_html, "html.parser")
        return None
    except Exception as e:
        print(f"Error fetching page content: {str(e)}")
        return None

def get_page_title_by_id(page_id: str):
    try:
        return confluence.get_page_by_id(page_id).get("title", "")
    except Exception as e:
        print(f"Error fetching pae title: {str(e)}")
        return None

# print(get_all_confluence_urls("https://error-402.atlassian.net/wiki/spaces/~6283b562d9ddcc006e9cee7c/"))
# print(get_all_confluence_data("https://error-402.atlassian.net/wiki/spaces/~6283b562d9ddcc006e9cee7c/pages/131302/Fraud+Detection+API+Schema"))
# print(get_all_confluence_data("https://error-402.atlassian.net/wiki/spaces/~6283b562d9ddcc006e9cee7c/folder/98469?atlOrigin=eyJpIjoiOTQ4YzBkMTQ1N2Q4NDExMWJmMGQzMDE3ODc1ZjIyOTAiLCJwIjoiYyJ9"))