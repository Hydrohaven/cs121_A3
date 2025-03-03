import json
import re
import time
import numpy as np
import requests
from fpdf import FPDF
from nltk.stem import PorterStemmer

class SearchEngine:
    def __init__(self, index_path):
        """
        Initializes the search engine.

        - index_path: Path to final_index.json (the inverted index).
        """
        self.index_path = index_path
        self.stemmer = PorterStemmer()

        self._start_time = time.perf_counter() # starts timer
        print("Loading inverted index...")

        self.index = self.load_index()

        self._elapsed_time = time.perf_counter() - self._start_time # ends timer
        print(f"Elapsed time: {self._elapsed_time:0.4f} seconds")

    
    def start_timer(self):
        """Starts timer"""
        self._start_time = time.perf_counter()  # Force reset


    def end_timer(self, *, output: bool = True):
        """Ends timer, will print elapsed time if parameter output is True"""
        if self._start_time:
            self._elapsed_time = time.perf_counter() - self._start_time # ends timer
            if output: 
                print(f"Elapsed time: {self._elapsed_time:0.6f} seconds")

            self._start_time = None
        else:
            print("Timer isn't running yet!")


    def load_index(self):
        """Loads the inverted index from final_index.json."""
        with open(self.index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
        

    def tokenize_and_stem(self, query):
        """Tokenizes and stems a search query."""
        pass


    def boolean_and_search(self, query):
        """Processes a Boolean AND search and ranks results using Cosine Similarity."""
        pass


    def _check_url_validity(self, url):
        """Returns True if the URL is accessible (not a 404 page), otherwise False."""
        try:
            response = requests.head(url, allow_redirects=True, timeout=3)  # Send a lightweight HEAD request
            # print("URL:", url, "HTTP RESPONSE:", response) # DEBUG STATEMENT
            return response.status_code == 200  # Only return True for 200 OK responses
        except requests.RequestException:
            return False  # Handles timeouts, connection errors, etc.


    def search(self, query):
        """Performs a search and returns the top 5 document URLs."""
        pass


    def generate_report(self):
        """Generates a PDF report containing the top 5 search results for predefined queries."""
        


if __name__ == "__main__":
    search_engine = SearchEngine("partial/final_index.json")

    choice = input("\nWould you like to run the searcher or generate the report (run/report)?: ").strip()
    if choice == "report":
        search_engine.generate_report()
    elif choice == "run":
        while True:
            query = input("\nEnter your search query (or type 'exit' to quit): ").strip()
            if query.lower() == "exit":
                print("Exiting search.")
                break

            search_engine.search(query)
