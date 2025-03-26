from langgraph_sdk import get_sync_client

# url="http://localhost:2024"
# client= get_sync_client(url="http://localhost:2024")


# assistant_id="12154be0-d2dc-4e8d-860c-68291d3a54d4"

async def get_assistant_id(client, assistant_id):
    assistant = None  # Define assistant upfront to avoid unbound variable issues
    
    try:
        # Try to fetch the existing assistant
        assistant = await client.assistants.get(assistant_id=assistant_id)
    except Exception as e:
        print(f"Error: {e}. Creating a new assistant...")
        
        try:
            # Attempt to create a new assistant
            assistant = await client.assistants.create(
                graph_id="agent",
                name="visionQA"
            )
        except Exception as e:
            print(f"Cannot create an assistant. Server might be down. Error: {e}")
            return None  # Explicitly return None if creation fails
    if assistant:
    # Check if the assistant object is a dictionary
        if isinstance(assistant, dict) and "assistant_id" in assistant:
            assistant_id = assistant["assistant_id"]
        elif hasattr(assistant, "assistant_id"):
            assistant_id = assistant.assistant_id
        else:
            print("No assistant_id found.")
            assistant_id = None
    print("Assistant Id Loaded:", assistant_id)
    return assistant_id



async def get_thread_id(client, thread_id):
    thread = None 
    try:
        # Try to fetch the existing assistant
        thread = await client.threads.get(thread_id)
    except Exception as e:
        print(f"Error: {e}. Creating a new thread...")
        
        try:
            # Attempt to create a new assistant
            thread = await client.threads.create(
                if_exists="raise"
            )
        except Exception as e:
            print(f"Cannot create a thread. Server might be down. Error: {e}")
            return None  # Explicitly return None if creation fails
    if thread:
    # Check if the assistant object is a dictionary
        if isinstance(thread, dict) and "thread_id" in thread:
            thread_id = thread["thread_id"]
        elif hasattr(thread, "thread_id"):
            thread_id = thread.thread_id
        else:
            print("No assistant_id found.")
            thread_id = None
    print(thread_id)
    return thread_id


async def query(client, assistant_id, thread_id,query):

    print(thread_id,assistant_id)
    final_state_of_run=None
    try:
        final_state_of_run = await client.runs.wait(
        thread_id=thread_id,
        assistant_id=assistant_id,
        input={"question": query}
        )
    except Exception as e:
        print(f"Error during query: {e}")
    return final_state_of_run


# thread_id=get_thread_id(client,"e15064e1-78ba-4a68-86fe-235404ac9eab")
# response=query(client,assistant_id,thread_id,"Hello")
# print(response)


    

    






