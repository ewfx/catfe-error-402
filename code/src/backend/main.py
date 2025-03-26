from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
from utils.SemanticChunking import semantic_chunking
from data_extraction.confluence import get_all_confluence_data, get_page_title_by_id, get_page_soup
from models.embedding import generate_embeddings
from utils.utils import chunk_to_text, chunk_to_text_llama
from pydantic import BaseModel
# import numpy as np
from utils.post_vdb import post_embeddings
from process_links import process_links
from bdd.get_step_defs import get_step_defs
# from utils import chunking_script
import os
from dotenv import load_dotenv
from langgraph_sdk import get_client
from utils.langgraph_api import get_assistant_id, get_thread_id, query
from utils.generate_bdd_prompt import get_prompt
from utils.extract_gherkin import extract_gherkin_scenarios

# Load environment variables
load_dotenv()

ALLURE_BASE_URL = os.getenv("ALLURE_BASE_URL")

app = FastAPI()

# ✅ CORS middleware (same as Flask's CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict it to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConfluenceRequest(BaseModel):
    url: str

class EmbeddingRequest(BaseModel):
    embeddings: list
    metadata: list

class URLsRequest(BaseModel):
    urls: list

class AppRequest(BaseModel):
    endpoints: list
    base_url: str
    application_name: str

class BddRequest(BaseModel):
    endpoints: list
    base_url: str
    bdd_list: list
    application_name: str
    api_schema: str


class ChatRequest(BaseModel):
    message: str
    thread_id: str= ""

client = None
assistant_id = None

@app.on_event("startup")
async def init_services():
    """Initialize sync services."""
    global client, assistant_id
    url = "http://192.168.1.17:2024"
    
    # Sync client initialization
    client = get_client(url=url)
    assistant_id = await get_assistant_id(client, "12154be0-d2dc-4e8d-860c-68291d3a54d4")
    

@app.get("/")
def home():
    return "Error-402"

# @app.post("/get_embeddings")
# async def get_embeddings(request: ConfluenceRequest):
#     try:
#         print(request.url)
#         pages = get_all_confluence_data(request.url)
#         all_embeddings = np.array([]).reshape(0, 768)
#         metadata = []
#         structured_content = []

#         for page in pages:
#             page_title = get_page_title_by_id(page.get("page_id"))
#             print(page_title)
#             # print(page)
#             # Perform semantic chunking for each page
#             chunks = semantic_chunking(page)
#             for chunk in chunks:
#                 print(chunk)
#                 structured_content.append(chunk_to_text(chunk))
#                 metadata.append({"title": page_title, "type": chunk.get("metadata").get("type")})
#                 if chunk.get("heading"):
#                     metadata[-1]["heading"] = chunk.get("heading")
#             structured_content = [chunk_to_text(chunk) for chunk in chunks]
#             for i, content in enumerate(structured_content):
#                 metadata[i]["text"] = content
#             embeddings = generate_embeddings(structured_content)
#             all_embeddings = np.concatenate((embeddings, all_embeddings), axis=0)

#         return {"embeddings": all_embeddings.tolist(), "metadata": metadata}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/get_embeddings")
# async def get_embeddings(request: ConfluenceRequest):
#     try:
#         print(request.url)
#         pages = get_all_confluence_data(request.url)
#         all_embeddings = np.array([]).reshape(0, 768)
#         metadata = []
#         structured_content = []

#         for page in pages:
#             page_title = get_page_title_by_id(page.get("page_id"))
#             print(page_title)
#             # print(page)
#             # Perform semantic chunking for each page
#             try:
#                 chunks = semantic_chunking(page)
#             except Exception as e:
#                 print(e)
#             for chunk in chunks:
#                 # print(chunk)
#                 # print(chunk_to_text(chunk))
#                 structured_content.append(chunk_to_text(chunk))
#                 # print(structured_content)
#                 metadata.append({"title": page_title, "importance": chunk.get("metadata").get("importance"), "type": chunk.get("metadata").get("type")})
#                 if chunk.get("heading"):
#                     metadata[-1]["heading"] = chunk.get("heading")
#             # print(len(structured_content))
#             # structured_content = [chunk_to_text(chunk) for chunk in chunks]
#             for i, content in enumerate(structured_content):
#                 metadata[i]["text"] = content
#             embeddings = generate_embeddings(structured_content)
#         all_embeddings = np.concatenate((embeddings, all_embeddings), axis=0)

#         print(metadata)

#         print(len(all_embeddings), len(metadata))
#         return {"embeddings": all_embeddings.tolist(), "metadata": metadata}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_embeddings")
async def get_embeddings(request: URLsRequest):
    try:
        return process_links(request.urls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/post_in_vdb")
async def post_in_vdb(request: EmbeddingRequest):
    try:
        post_embeddings(request.embeddings, request.metadata)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/post_embeddings")
async def post_embeddings_endpoint(request: URLsRequest):
    try:
        client = TestClient(app)
        embeddings_response = client.post("/get_embeddings", json=request.dict())
        print("Embeddings Generated")
        if embeddings_response.status_code != 200:
            raise HTTPException(status_code=embeddings_response.status_code, detail="Error fetching embeddings")
        embeddings_data = embeddings_response.json()
        print("Got the Embeddings Data", len(embeddings_data["embeddings"]))

        post_vdb_response = client.post("/post_in_vdb", json=embeddings_data)

        print(post_vdb_response)

        if post_vdb_response.status_code != 200:
            raise HTTPException(status_code=post_vdb_response.status_code, detail="Error posting embeddings to VDB")

        return {"status": "embeddings generated and posted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/generate_bdd")
async def generate_bdd(request: AppRequest):
    try:
        prompt = get_prompt(endpoints=request.endpoints, base_url=request.base_url, application_name=request.application_name)
        thread_id = await get_thread_id(client, None)
        assistant_response = await query(client, assistant_id, thread_id, prompt)
        if not assistant_response:
            raise HTTPException(status_code=500, detail="No response from assistant")

        response_content = (
            assistant_response.get("generation", {}).get("content")
            if isinstance(assistant_response, dict)
            else str(assistant_response)
        )
        print(response_content)

        final_content = extract_gherkin_scenarios(response_content)
        print(final_content)
        return {
            "thread_id": thread_id,
            "response": final_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # try:
    #     client = TestClient(app)
    #     return client.post("/chat", json={"message": prompt})
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_reports")
async def generate_reports(request: BddRequest):
    # Call the methods inside the BDD folder to generate all the BDDs
    try:
        is_html_generated = get_step_defs(BDDs=request.bdd_list, base_url=request.base_url, endpoints=request.endpoints, application_name=request.application_name, api_schema=request.api_schema)
        if is_html_generated:
            return f"{ALLURE_BASE_URL}/{request.application_name}/html/index.html"
        raise HTTPException(status_code=500, detail="Report not generated")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        message = request.message
        thread_id = request.thread_id

        if not message:
            raise HTTPException(status_code=400, detail="A 'message' is required")

        # ✅ Use sync functions for client operations
        thread_id = await get_thread_id(client, thread_id) if thread_id else await get_thread_id(client, None)

        if not thread_id:
            raise HTTPException(status_code=500, detail="Failed to retrieve or create a thread")

        # ✅ Async assistant query
        assistant_response = await query(client, assistant_id, thread_id, message)

        if not assistant_response:
            raise HTTPException(status_code=500, detail="No response from assistant")

        # ✅ Extract content safely
        response_content = (
            assistant_response.get("generation", {}).get("content")
            if isinstance(assistant_response, dict)
            else str(assistant_response)
        )

        return {
            "thread_id": thread_id,
            "response": response_content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal server error occurred")