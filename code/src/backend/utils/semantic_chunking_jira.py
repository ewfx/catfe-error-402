import json
import re

# Chunk size constraints (suggested limits)
MAX_WORDS = 300
MIN_WORDS = 150

def load_json(filename):
    """Load JSON data from a file."""
    with open(filename, 'r') as file:
        return json.load(file)

def count_words(text):
    """Count the number of words in the text."""
    return len(text.split())

def is_redundant(key, value):
    """Check if a key-value pair is redundant."""
    # Static redundant keys that are always irrelevant
    static_redundant_keys = [
        "avatarUrls", "iconUrl", "self", "id", "accountId", "entityId",
        "hierarchyLevel", "accountType", "timeZone", "active"
    ]

    # Keys that are redundant only if they are empty
    conditional_redundant_keys = [
        "watchers", "worklogs", "votes", "comments", "attachment", 
        "timetracking", "progress", "aggregateprogress", "worklog",
        "issuerestriction"
    ]

    # Check for static redundant keys
    if any(static_key in key for static_key in static_redundant_keys):
        return True
    
    # Check for conditional redundant keys (only if empty)
    if any(cond_key in key for cond_key in conditional_redundant_keys) and (value == "" or value == {} or value == [] or value is None):
        return True

    return False

def clean_json(data):
    """Recursively remove redundant fields from JSON data."""
    if isinstance(data, dict):
        cleaned_data = {}
        for key, value in data.items():
            if not is_redundant(key, value):
                cleaned_value = clean_json(value)
                if cleaned_value not in [None, "", {}, []]:
                    cleaned_data[key] = cleaned_value
        return cleaned_data
    elif isinstance(data, list):
        cleaned_list = [clean_json(item) for item in data if item not in [None, "", {}, []]]
        return cleaned_list
    else:
        return data

def clean_key_name(key):
    """Remove redundant prefixes from keys."""
    # print("Before Clean: ", key)
    key = re.sub(r'^(fields|customfield_\d*)\.', '', key)
    key = re.sub(r'\.self|\.id|\.accountId|\.avatarUrls|\.iconUrl|\.entityId|\.shouldDisplay', '', key)
    # print("After Clean: ", key)
    return key

def flatten_dict(d, parent_key='', sep='.'):
    """Flatten a nested dictionary with cleaned key names."""
    items = []
    for k, v in d.items():
        # cleaned_key = clean_key_name(k)
        # print(cleaned_key)
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        # print(new_key)
        new_key = clean_key_name(new_key)
        # print("Cleaned Key: ", new_key)
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for idx, item in enumerate(v):
                list_key = f"{new_key}[{idx}]"
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, list_key, sep=sep).items())
                else:
                    items.append((list_key, str(item)))
        else:
            items.append((new_key, str(v)))
    return dict(items)

def create_chunk(key, value):
    """Create a formatted chunk string."""
    return f"{key}: {value}"

def get_application_name(project_key, app_map):
    """Retrieve the application name based on the project key."""
    return app_map.get(project_key, "Unknown Application")

def semantic_chunking(jira_data, app_map, public_url):
    """Perform semantic chunking and return as a list of strings with metadata."""
    project_key = jira_data.get("key", "Unknown").split("-")[0]
    application_name = get_application_name(project_key, app_map)
    ticket_key = jira_data.get("key", "Unknown")

    cleaned_data = clean_json(jira_data)
    flattened_data = flatten_dict(cleaned_data)
    chunks = []
    current_chunk = ""

    for key, value in flattened_data.items():
        line = create_chunk(key, value)

        # Check if adding the line exceeds the max word limit
        if count_words(current_chunk + line) > MAX_WORDS:
            # Save the current chunk if it meets the min word limit
            if count_words(current_chunk) >= MIN_WORDS:
                chunk_metadata = {
                    "ticket_key": ticket_key,
                    "application": application_name,
                    "url": public_url,
                    "text": current_chunk.strip()
                }
                chunks.append(chunk_metadata)
                current_chunk = ""

        current_chunk += line + "\n"

    # Add the last remaining chunk
    if current_chunk:
        chunk_metadata = {
            "ticket_key": ticket_key,
            "application_name": application_name,
            "url": public_url,
            "text": current_chunk.strip()
        }
        chunks.append(chunk_metadata)

    return chunks

def save_chunks(chunks, filename):
    """Save the generated chunks to a JSON file."""
    with open(filename, "w") as file:
        json.dump(chunks, file, indent=4)
    print(f"Chunks saved to {filename}")

def main():
    # Load JIRA data from JSON file
    jira_data = load_json("jira_response.json")

    # Load application map from a JSON file
    app_map = load_json("application_map.json")

    # Public URL of JIRA (you can pass it as a parameter)
    public_url = "https://error-402.atlassian.net/browse/CCS-8"

    # Perform semantic chunking
    chunks = semantic_chunking(jira_data, app_map, public_url)

    # Save chunks to a file
    save_chunks(chunks, "jira_semantic_chunks.json")

    # Print a sample chunk for verification
    print("Sample Chunk:")
    print(json.dumps(chunks[0], indent=4))

if __name__ == "__main__":
    main()
