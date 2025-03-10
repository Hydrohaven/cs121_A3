import os
import boto3
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import time
from search import SearchEngine
import uvicorn
# import aiohttp
# import asyncio

# Set up AWS S3 client using your AWS credentials (either through environment variables or hardcoded)
s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),  # From environment variables
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),  # From environment variables
)

# S3 bucket details
bucket_name = "my-fastapi-indexes"  
s3_file_name = "final_index.json"
index_path = "final_index.json"

# Function to download the file from S3
def download_index_from_s3():
    try:
        print(f"Downloading {s3_file_name} from S3...")
        s3.download_file(bucket_name, s3_file_name, index_path)
        print(f"Downloaded {s3_file_name} successfully!")
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        raise

# Ensure that the final_index.json exists, or regenerate/download it
if not os.path.exists(index_path):
    print(f"{index_path} not found, downloading from S3...")
    download_index_from_s3()


app = FastAPI()

# Initialize the search engine with the path to the final index
search_engine = SearchEngine("final_index.json")

# Jinja2 templates setup (for rendering HTML templates)
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Fetch content asynchronously
# async def fetch_content(session, url: str) -> str:
#     async with session.get(url) as response:
#         # If response is successful, extract content (assuming Wikipedia)
#         if response.status == 200:
#             return await response.text()
#         return ""

# # Summarize content asynchronously
# async def summarize_content(url: str) -> str:
#     async with aiohttp.ClientSession() as session:
#         content = await fetch_content(session, url)
#         return search_engine.summarize_document(content)

# @app.post("/search", response_class=HTMLResponse)
# async def search(request: Request, query: str = Form(...)):
#     start_time = time.perf_counter()

#     # Perform the search (returns a list of URLs or search results)
#     results = list(enumerate(search_engine.boolean_and_search(query), 1))[:50]

#     # Create a list of tasks for summarizing each result
#     tasks = [summarize_content(result) for _, result in results]

#     # Use asyncio.gather to run the tasks concurrently
#     summarized_results = await asyncio.gather(*tasks)

#     # Package results with summaries
#     final_results = [
#         {"index": idx, "result": result, "summary": summary}
#         for (idx, result), summary in zip(results, summarized_results)
#     ]

#     elapsed_time = time.perf_counter() - start_time
#     formatted_elapsed_time = f"{elapsed_time:.4f}"

#     # Pass the summarized results to the template
#     return templates.TemplateResponse(
#         "index.html", {
#             "request": request,
#             "query": query,
#             "results": final_results,
#             "elapsed_time": formatted_elapsed_time
#         }
#     )

@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, query: str = Form(...)):
    start_time = time.perf_counter()
    results = list(enumerate(search_engine.boolean_and_search(query), 1))[:50]

    # Temporarily remove the summarization part
    summarized_results = []
    for idx, result in results:
        summarized_results.append({
            "index": idx,
            "result": result,
            "summary": ""  # Empty summary to isolate the problem
        })

    elapsed_time = time.perf_counter() - start_time
    formatted_elapsed_time = f"{elapsed_time:.4f}"

    return templates.TemplateResponse(
        "index.html", {"request": request, "query": query, "results": summarized_results, "elapsed_time": formatted_elapsed_time}
    )

if __name__ == "__main__":
    # Get the port from the environment variable or use 8000 as a fallback
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
