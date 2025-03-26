import json
from models.embedding import generate_embeddings
from utils.SemanticChunking import semantic_chunking
from data_extraction.confluence import get_all_confluence_data, get_page_title_by_id
from utils.utils import chunk_to_text
import numpy as np

def process_confluence_links(confluence_urls):
    """
    Process Confluence links to extract data, generate chunks, and calculate embeddings.

    Args:
        confluence_url (str): URL of the Confluence page or space.
        app_map (dict): A dictionary mapping project keys to application names.

    Returns:
        dict: A dictionary containing the processed chunks and embeddings.
    """
    urls_processed = []
    metadata = []
    all_embeddings = np.array([]).reshape(0, 768)

    for confluence_url in confluence_urls:
        if confluence_url in urls_processed:
            continue
        try:
            # Step 1: Get all confluence data (including nested pages or spaces)
            confluence_pages = get_all_confluence_data(confluence_url)
            structured_content = []

            for confluence_page in confluence_pages:
                page_url = confluence_page.get("url")
                if page_url in urls_processed:
                    continue
                urls_processed.append(page_url)
                soup = confluence_page.get("soup")
                page_title = get_page_title_by_id(confluence_page.get("page_id"))

                print(f"Processing Confluence URL: {page_url}")

                if soup:
                    # Step 2: Generate semantic chunks from Confluence data
                    chunks = semantic_chunking(confluence_page)
                    for chunk in chunks:
                        structured_content.append(chunk_to_text(chunk))
                        metadata.append({"text":structured_content[-1],"title": page_title, "importance": chunk.get("metadata").get("importance"), "type": chunk.get("metadata").get("type"), "url": page_url})
                        if chunk.get("heading"):
                            metadata[-1]["heading"] = chunk.get("heading")
                    embeddings = generate_embeddings(structured_content)
                    print(f"Generated embeddings for Confluence page {page_url}")
                else:
                    print(f"No valid content found for URL: {page_url}")
                all_embeddings = np.concatenate((embeddings, all_embeddings), axis=0)


        except Exception as e:
            print(f"Error processing Confluence URL {confluence_url}: {str(e)}")

    
    return {"embeddings": all_embeddings.tolist(), "metadata": metadata}

# Example Usage
if __name__ == "__main__":
    confluence_urls = ["https://error-402.atlassian.net/wiki/spaces/~6283b562d9ddcc006e9cee7c/pages/131302/Fraud+Detection+API+Documentation"]

    chunks = process_confluence_links(confluence_urls)
    print(json.dumps(chunks, indent=4))
