import json
import re
import time
import numpy as np
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

    def load_index(self):
        """Loads the inverted index from final_index.json."""
        pass
        

    def tokenize_and_stem(self, query):
        """Tokenizes and stems a search query."""
        pass

    def boolean_and_search(self, query):
        """Processes a Boolean AND search and ranks results using Cosine Similarity."""
        pass

    def search(self, query):
        """Performs a search and returns the top 5 document URLs."""
        pass

if __name__ == "__main__":
    search_engine = SearchEngine("partial/final_index.json")

    while True:
        query = input("\nEnter your search query (or type 'exit' to quit): ").strip()
        if query.lower() == "exit":
            print("Exiting search.")
            break

        search_engine.search(query)
