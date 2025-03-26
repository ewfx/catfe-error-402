# from utils.image_processing import process_image

# def semantic_chunking(page_data):
#     chunks = []
#     current_chunk = None
#     soup = page_data.get("soup")
#     page_id = page_data.get("page_id")

#     content_div = soup.find('div', {'class': 'content'}) or soup
#     for elem in content_div.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'code', 'img', 'ac:image', 'ac:structured-macro']):

#         # Handle headings
#         if elem.name in ['h1', 'h2', 'h3', 'h4']:
#             if current_chunk:
#                 chunks.append(current_chunk)
#             current_chunk = {
#                 "heading": elem.get_text(strip=True),
#                 "content": [],
#                 "metadata": {"type": "heading"}
#             }

#         # Handle structured macros (code blocks)
#         elif elem.name == 'ac:structured-macro':
#             code_body = elem.find('ac:plain-text-body')
#             if code_body:
#                 code_text = code_body.get_text(strip=True)
#                 if current_chunk:
#                     current_chunk["content"].append({
#                         "type": "json_schema",
#                         "data": code_text
#                     })

#         # Handle text elements
#         elif elem.name in ['p', 'ul', 'ol', 'code']:
#             if not current_chunk:
#                 current_chunk = {
#                     "heading": "General",
#                     "content": [],
#                     "metadata": {"type": "general"}
#                 }
#             text = elem.get_text(strip=True)
#             current_chunk["content"].append({"type": "text", "data": text})

#         # Handle images
#         elif elem.name in ['img', 'ac:image']:
#             image_summary = process_image(elem, page_id)
#             if current_chunk:
#                 current_chunk["content"].append({
#                     "type": "diagram",
#                     "data": f"[IMAGE SUMMARY: {image_summary}]"
#                 })

#     # Append the final chunk
#     if current_chunk:
#         chunks.append(current_chunk)

#     return chunks


from utils.image_processing import process_image

HIGH_IMPORTANCE_KEYWORDS = [
    "API Details", "Endpoint", "BDD Test"
]
MEDIUM_IMPORTANCE_KEYWORDS = ["Example", "Scenario", "Response", "Request"]
LOW_IMPORTANCE_KEYWORDS = ["Enhancements", "Future Considerations"]

MAX_TOKENS = 500
MIN_TOKENS = 200
MAX_WORDS = 300
MIN_WORDS = 150

def determine_importance(heading):
    heading_lower = heading.lower()
    if any(keyword.lower() in heading_lower for keyword in HIGH_IMPORTANCE_KEYWORDS):
        return 1.0
    elif any(keyword.lower() in heading_lower for keyword in MEDIUM_IMPORTANCE_KEYWORDS):
        return 0.7
    elif any(keyword.lower() in heading_lower for keyword in LOW_IMPORTANCE_KEYWORDS):
        return 0.4
    return 0.5  # Default importance

def calculate_tokens(text):
    """Estimate the number of tokens based on word count."""
    if isinstance(text, list):
        # Flatten the list recursively and join all strings
        return sum(calculate_tokens(item) for item in text)
    if isinstance(text, dict):
        # Recursively process dictionary values
        return sum(calculate_tokens(v) for v in text.values())
    if isinstance(text, str):
        # Return the number of words in the string
        return len(text.split())
    return 0  # Return 0 for unrecognized types

def flatten_content(content):
    """Recursively flatten content and join all strings."""
    if isinstance(content, list):
        return " ".join(flatten_content(item) for item in content)
    if isinstance(content, dict):
        return " ".join(flatten_content(v) for v in content.values())
    if isinstance(content, str):
        return content
    return ""

def flatten_chunk_content(content):
    """Recursively flatten chunk content to extract all text data."""
    flat_content = []

    def _flatten(item):
        if isinstance(item, str):
            flat_content.append(item)
        elif isinstance(item, dict):
            for key, value in item.items():
                _flatten(value)
        elif isinstance(item, list):
            for subitem in item:
                _flatten(subitem)

    _flatten(content)
    return " ".join(flat_content)





def split_large_chunk(chunk):
    """Split a large chunk into smaller subchunks if it exceeds token/word limits."""
    content = chunk["content"]
    subchunks = []
    subchunk = {"heading": chunk["heading"], "content": [], "metadata": chunk["metadata"]}

    for part in content:
        subchunk["content"].append(part)
        current_text = flatten_chunk_content(subchunk["content"])
        token_count = calculate_tokens(current_text)

        if token_count > MAX_TOKENS or len(current_text.split()) > MAX_WORDS:
            # Remove the last added part and save the current subchunk
            subchunk["content"].pop()
            subchunks.append(subchunk)
            # Start a new subchunk with the current part
            subchunk = {"heading": chunk["heading"], "content": [part], "metadata": chunk["metadata"]}

    # Add the last chunk if not empty
    if subchunk["content"]:
        subchunks.append(subchunk)

    return subchunks

def semantic_chunking(page_data):
    chunks = []
    current_chunk = None
    soup = page_data.get("soup")
    page_id = page_data.get("page_id")

    content_div = soup.find('div', {'class': 'content'}) or soup

    for elem in content_div.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'code', 'img', 'ac:image', 'ac:structured-macro']):

        # Handle headings
        if elem.name in ['h1', 'h2']:
            if current_chunk:
                # current_chunk["metadata"]["importance"] = determine_importance(current_chunk["heading"])
                flattened_content = flatten_chunk_content(current_chunk["content"])
                if  calculate_tokens(flattened_content) > MAX_TOKENS:
                    print("Splitting Chunk")
                    print(current_chunk)
                    chunks.extend(split_large_chunk(current_chunk))
                elif MIN_TOKENS <= calculate_tokens(flattened_content):
                    print(current_chunk)
                    chunks.append(current_chunk)
                else:
                    print("Less than min token: ", calculate_tokens(flattened_content))
                    print(current_chunk)
                    current_chunk["content"].append({
                        "type": "subsection",
                        "data": [],
                        "heading": elem.get_text(strip=True)
                    })
                    continue

            current_chunk = {
                "heading": elem.get_text(strip=True),
                "content": [],
                "metadata": {"type": "section", "importance": 1.0}
            }
        
        elif elem.name in ['h3']:
            if not current_chunk or current_chunk["heading"] == "General":
                current_chunk = {
                    "heading": elem.get_text(strip=True),
                    "content": [],
                    "metadata": {"type": "section", "importance": 0.7}
                }
            else:
                current_chunk["content"].append({
                    "type": "subsection",
                    "data": [],
                    "heading": elem.get_text(strip=True)
                })
        
        elif elem.name=='h4':
            if not current_chunk or current_chunk["heading"] == "General":
                current_chunk = {
                    "heading": elem.get_text(strip=True),
                    "content": [],
                    "metadata": {"type": "section", "importance": 0.5}
                }
            elif len(current_chunk["content"])>0 and isinstance(current_chunk["content"][-1], dict):
                current_chunk["content"][-1]["data"].append({
                    "type": "sub-subsection",
                    "data": [],
                    "heading": elem.get_text(strip=True)
                })
            else:
                current_chunk["content"].append({
                    "type": "subsection",
                    "data": [],
                    "heading": elem.get_text(strip=True)
                })

        # Handle structured macros (code blocks)
        elif elem.name == 'ac:structured-macro':
            code_body = elem.find('ac:plain-text-body')
            if code_body:
                code_text = code_body.get_text(strip=True)
                curr_chunk_data = {
                    "type": "json_schema",
                    "data": code_text
                }
                if current_chunk:
                    content_length = len(current_chunk["content"])
                    if content_length > 0 and isinstance(current_chunk["content"][-1], dict):
                        if "data" in current_chunk["content"][-1] and isinstance(current_chunk["content"][-1]["data"], list):
                            current_chunk["content"][-1]["data"].append(curr_chunk_data)
                        else:
                            current_chunk["content"].append(curr_chunk_data)
                    else:
                        current_chunk["content"].append(curr_chunk_data)

        # Handle text elements
        elif elem.name in ['p', 'ul', 'ol', 'code']:
            text = elem.get_text(strip=True)
            if text:
                curr_chunk_data = {
                    "type": "text",
                    "data": text
                }
                if not current_chunk:
                    current_chunk = {
                        "heading": "General",
                        "content": [curr_chunk_data],
                        "metadata": {"type": "general"}
                    }
                else:
                    content_length = len(current_chunk["content"])
                    if content_length > 0 and isinstance(current_chunk["content"][-1], dict):
                        if "data" in current_chunk["content"][-1] and isinstance(current_chunk["content"][-1]["data"], list):
                            current_chunk["content"][-1]["data"].append(curr_chunk_data)
                        else:
                            current_chunk["content"].append(curr_chunk_data)
                    else:
                        current_chunk["content"].append(curr_chunk_data)

        # Handle images
        elif elem.name in ['img', 'ac:image']:
            image_summary = process_image(elem, page_id)
            if(image_summary):
                curr_chunk_data = {
                    "type": "Image",
                    "data": f"[IMAGE SUMMARY: {image_summary}]"
                }
                if not current_chunk:
                    current_chunk = {
                        "heading": "Image",
                        "content": [curr_chunk_data],
                        "metadata": {"type": "image"}
                    }
                else:
                    content_length = len(current_chunk["content"])
                    if content_length > 0 and isinstance(current_chunk["content"][-1], dict):
                        if "data" in current_chunk["content"][-1] and isinstance(current_chunk["content"][-1]["data"], list):
                            current_chunk["content"][-1]["data"].append(curr_chunk_data)
                        else:
                            current_chunk["content"].append(curr_chunk_data)
                    else:
                        current_chunk["content"].append(curr_chunk_data)

    # Append the final chunk
    if current_chunk:
        current_chunk["metadata"]["importance"] = determine_importance(current_chunk["heading"])
        flattened_content = flatten_chunk_content(current_chunk["content"])
        if calculate_tokens(flattened_content) > MAX_TOKENS:
            print("Splitting Chunk")
            print(current_chunk)
            chunks.extend(split_large_chunk(current_chunk))
        elif calculate_tokens(flattened_content):
            print(current_chunk)
            chunks.append(current_chunk)

    return chunks
