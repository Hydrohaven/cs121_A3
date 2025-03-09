import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import time
from search import SearchEngine
import uvicorn


app = FastAPI()

# Initialize the search engine with the path to the final index
search_engine = SearchEngine("partial_test/final_index.json")

# Jinja2 templates setup (for rendering HTML templates)
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, query: str = Form(...)):
    start_time = time.perf_counter()
    results = list(enumerate(search_engine.boolean_and_search(query), 1))
    elapsed_time = time.perf_counter() - start_time
    formatted_elapsed_time = f"{elapsed_time:.4f}"

    return templates.TemplateResponse(
        "index.html", {"request": request, "query": query, "results": results, "elapsed_time": formatted_elapsed_time}
    )


@app.get("/generate_report", response_class=FileResponse)
async def generate_report():
    search_engine.generate_report()
    return FileResponse("search_report.pdf", media_type="application/pdf", filename="search_report.pdf")

if __name__ == "__main__":
    # Get the port from the environment variable or use 8000 as a fallback
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
