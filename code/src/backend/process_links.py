import json
import re
from utils.segregate_links import segregate_links
from process_jira import process_jira_links
from process_confluence import process_confluence_links

APP_MAP = {
        "CCS": "Fraud Detection"
    }

def process_links(links, app_map=APP_MAP):
    """
    Process given links, segregate them, and handle JIRA links separately.
    
    Args:
        links (list): A list of URLs to be processed.
        app_map (dict): A dictionary mapping project keys to application names.

    Returns:
        dict: A dictionary containing the processed chunks.
    """
    # Step 1: Segregate the links
    link_categories = segregate_links(links)
    jira_urls = link_categories["jira_links"]
    confluence_urls = link_categories["confluence_links"]

    # Step 2: Process JIRA links
    jira_chunks = process_jira_links(jira_urls, app_map)
    confluence_chunks = process_confluence_links(confluence_urls)

    embeddings = jira_chunks["embeddings"] + confluence_chunks["embeddings"]
    metadata = jira_chunks["metadata"] + confluence_chunks["metadata"]

    return {"embeddings": embeddings, "metadata": metadata}

# Example Usage
if __name__ == "__main__":
    # Example links
    links = [
        "https://error-402.atlassian.net/browse/CCS-8",
        "https://error-402.atlassian.net/browse/CCS-7",
        "https://error-402.atlassian.net/wiki/spaces/~6283b562d9ddcc006e9cee7c/pages/131302/Fraud+Detection+API+Documentation"
    ]

    chunks = process_links(links)
    print(json.dumps(chunks, indent=4))
