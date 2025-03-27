import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import time
from search import SearchEngine
import uvicorn
from transformers import pipeline
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Initialize the search engine with the path to the final index
search_engine = SearchEngine("partial_test/final_index.jsonl")

# Jinja2 templates setup (for rendering HTML templates)
templates = Jinja2Templates(directory="templates")

# Initialize a pipeline for summarization
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)

def fetch_page_content(url):
    """Fetch the main content of a web page using BeautifulSoup."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Get all text from the page 
        paragraphs = soup.find_all("p")  # Extract all paragraph tags
        text = ' '.join([para.get_text() for para in paragraphs if para.get_text()])
        
        return text
    
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return ""


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, query: str = Form(...)):
    start_time = time.perf_counter()
    results = list(enumerate(search_engine.boolean_and_search(query), 1))[:50]

    summarized_results = []
    for idx, result in results:
        result_text = fetch_page_content(result)

        if result_text:
            if len(result_text.split()) > 50: # summarize if longer than 50 words
                summary = summarizer(result_text, max_length=70, min_length=20, do_sample=False)
                summarized_results.append({
                    "index": idx,
                    "result": result,
                    "summary": summary[0]['summary_text'],
                })
            else: 
                summarized_results.append({
                    "index": idx,
                    "result": result,
                    "summary": result_text,
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