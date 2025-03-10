import json
import re
import time
import numpy as np
import requests
from fpdf import FPDF
from nltk.stem import PorterStemmer
from transformers import pipeline

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

    def generate_ngrams(self, tokens, n):
        """Generate n-grams from a list of tokens."""
        return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
        

    def tokenize_and_stem(self, query):
        """Tokenizes and stems a search query."""
        words = re.findall(r'\b[a-zA-Z0-9]+\b', query.lower())  # Extract words
        stemmed_words = [self.stemmer.stem(word) for word in words]  

        bigrams = [" ".join(words[i:i+2]) for i in range(len(words) - 1)]
        trigrams = [" ".join(words[i:i+3]) for i in range(len(words) - 2)]

        return stemmed_words + bigrams + trigrams  # Apply stemming


    def boolean_and_search(self, query):
        """Processes a Boolean AND search and ranks results using Cosine Similarity."""
        query_terms = self.tokenize_and_stem(query)
        if not query_terms:
            return [] 
        
        # get posting list for each term
        posting_list = [set(self.index.get(term, {}).keys()) for term in query_terms]
        common_docs = set.intersection(*posting_list) if posting_list else set()

        if not common_docs:
            return []
        
        # create doc vectors and query vector
        doc_vectors = {}
        query_vector = np.array([1] * len(query_terms)) # query vector is binary (each term contributes evenly)

        for doc_id in common_docs:
            doc_vectors[doc_id] = np.array([
                self.index[term][doc_id]["tf-idf"] if doc_id in self.index[term] else 0 for term in query_terms])
            
        # compute cosine similarity
        ranked_results = sorted(
            common_docs,
            key=lambda doc: np.dot(doc_vectors[doc], query_vector) / (np.linalg.norm(doc_vectors[doc]) * np.linalg.norm(query_vector) + 1e-9),  # Avoid division by zero
            reverse=True
        )

        return ranked_results


    def search(self, query):
        """Performs a search and returns the top 5 document URLs."""        
        self.start_timer()
        results = self.boolean_and_search(query)
        elapsed_time = time.perf_counter() - self._start_time

        for rank, doc_id in enumerate(results[:5], 1):
            print(f"{rank}. {doc_id}")
        
        print(f"Elapsed time: {elapsed_time:.6f} seconds")  # Print after query execution


    def generate_report(self):
        """Generates a PDF report containing the top 5 search results for predefined queries."""
        
        queries = [
            "Iftekhar Ahmed",
            "machine learning",
            "ACM",
            "master of software engineering"
        ]

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, "Search Engine Report", ln=True, align="C")
        pdf.ln(10)

        # Run each query and record results
        for query in queries:
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(200, 10, f"Query: {query}", ln=True)
            
            self.start_timer()
            results = self.boolean_and_search(query)
            elapsed_time = time.perf_counter() - self._start_time  # Capture time immediately after search

            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, f"Elapsed time: {elapsed_time:.6f} seconds", ln=True)
            pdf.ln(5)

            if not results:
                pdf.cell(200, 10, "No results found.", ln=True)
            else:
                for rank, doc_id in enumerate(results[:5], 1):
                    pdf.cell(200, 10, f"{rank}. {doc_id}", ln=True)

            pdf.ln(10)  # Add some space between queries

        # Save the report as a PDF file
        report_filename = "search_report.pdf"
        pdf.output(report_filename)
        print(f"Report saved as {report_filename}!")
        


if __name__ == "__main__":
    search_engine = SearchEngine("partial_test/final_index.json")

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
