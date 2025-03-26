import re
from data_extraction.jira import get_jira_ticket_details
from utils.semantic_chunking_jira import semantic_chunking, save_chunks
from models.embedding import generate_embeddings
import numpy as np

def process_jira_links(jira_urls, app_map):
    """
    Process JIRA links to extract data, generate chunks, and calculate embeddings.
    
    Args:
        jira_urls (list): A list of JIRA URLs.
        app_map (dict): A dictionary mapping project keys to application names.

    Returns:
        dict: A dictionary containing the processed chunks and embeddings.
    """
    all_embeddings = np.array([]).reshape(0, 768)
    metadata = []


    for jira_url in jira_urls:
        print(f"Processing JIRA URL: {jira_url}")

        ticket_key = None

        # Extract the ticket key from the JIRA URL
        match = re.search(r'/browse/([A-Z]+-\d+)', jira_url)
        if match:
            ticket_key = match.group(1)
        else:
            print(f"Invalid JIRA URL format: {jira_url}")
            continue
        
        # Step 2: Get JIRA ticket details
        try:
            jira_data = get_jira_ticket_details(ticket_key)
            if jira_data:
                print(f"Successfully fetched JIRA data for: {jira_url}")

                # Step 3: Generate semantic chunks from JIRA data
                chunks = semantic_chunking(jira_data, app_map, jira_url)
                ticket_key = jira_data.get("key", "unknown_ticket")

                # Save chunks to a file
                output_filename = f"chunks_{ticket_key}.json"
                save_chunks(chunks, output_filename)
                print(f"Chunks saved to: {output_filename}")

                chunk_texts = []

                # Step 4: Extract all chunk_text fields into a list
                for chunk in chunks:
                    chunk["type"] = "JIRA Ticket"
                    chunk_texts.append(chunk['text'])
                    metadata.append(chunk)

                # Step 5: Generate embeddings from chunk texts
                embeddings = generate_embeddings(chunk_texts)
                print(f"Generated embeddings for ticket {ticket_key}")
                all_embeddings = np.concatenate((embeddings, all_embeddings), axis=0)

                # Add embeddings to the final output
            else:
                print(f"Failed to fetch JIRA data for: {jira_url}")

        except Exception as e:
            print(f"Error processing JIRA URL {jira_url}: {str(e)}")

    return {"embeddings": all_embeddings.tolist(), "metadata": metadata}
