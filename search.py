import json
import re
import time
import numpy as np
import mmap
from fpdf import FPDF
from nltk.stem import WordNetLemmatizer
import nltk

# Ensure required NLTK resources are available
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)
debug = False

class SearchEngine:
    def __init__(self, index_path):
        """
        Initializes the search engine.

        - index_path: Path to final_index.jsonl (the inverted index in JSONL format).
        """
        self.index_path = index_path
        self.index_file = None  # File reference
        self.mmap_obj = None  # Memory-mapped file object
        self.lemmatizer = WordNetLemmatizer()

        print("Initializing memory-mapped index...")
        
        self.load_index()  # Load index with mmap


    def printd(self, msg):
        if debug: print(msg)


    def load_index(self):
        """Precomputes term offsets in the mmap file for faster searching."""
        self.index_file = open(self.index_path, "r", encoding="utf-8")
        self.mmap_obj = mmap.mmap(self.index_file.fileno(), 0, access=mmap.ACCESS_READ)

        self.term_offsets = {}  # Cache where each term starts
        start_time = time.perf_counter()

        with open(self.index_path, "r", encoding="utf-8") as f:
            while True:
                offset = f.tell()  # Save offset BEFORE reading the line
                line = f.readline()  # Manually read lines instead of `for line in f`
                if not line:
                    break  # Stop at end of file
                
                try:
                    term_data = json.loads(line.strip())  # Parse JSON line
                    if not isinstance(term_data, dict) or len(term_data) == 0:
                        continue  # Skip malformed entries
                    
                    term = list(term_data.keys())[0]  # Get term
                    self.term_offsets[term] = offset  # Store the file offset
                    
                except json.JSONDecodeError:
                    continue  # Skip malformed lines

        print(f"DEBUG: Precomputed {len(self.term_offsets)} term offsets for fast access.")
        elapsed_time = time.perf_counter() - start_time
        print(f"Time to precompute offsets: {elapsed_time:.6f} seconds")



    def get_postings(self, term):
        """Retrieves the postings list for a term using cached offsets."""
        term = term.lower()

        if term not in self.term_offsets:
            self.printd(f"DEBUG: Term `{term}` NOT found in index!")
            return {}

        # Jump to the precomputed offset
        self.mmap_obj.seek(self.term_offsets[term])
        line = self.mmap_obj.readline().decode("utf-8").strip()

        try:
            json_obj = json.loads(line)  # Parse the JSON line
            postings = json_obj.get(term, {})
            self.printd(f"DEBUG: Successfully parsed `{term}`. Found {len(postings)} documents.")
            
            return postings
        except json.JSONDecodeError:
            self.printd(f"DEBUG: JSON decoding failed for term `{term}`.")
            return {}


    def close(self):
        """Closes memory-mapped file."""
        if self.mmap_obj:
            self.mmap_obj.close()
        if self.index_file:
            self.index_file.close()


    def tokenize_and_lemmatize(self, query):
        """Tokenizes and lemmatizes a search query."""
        words = re.findall(r'\b[a-zA-Z0-9]+\b', query.lower())  # Extract words
        lemmatized_words = [self.lemmatizer.lemmatize(word) for word in words]  # Apply lemmatization

        self.printd(f"DEBUG: Query `{query}` tokenized to: {lemmatized_words}")
        return lemmatized_words


    def boolean_and_search(self, query):
        """Processes a Boolean AND search and ranks results using TF-IDF ranking."""
        query_terms = self.tokenize_and_lemmatize(query)
        if not query_terms:
            self.printd("DEBUG: Query contains no valid terms!")
            return []

        self.printd(f"DEBUG: Running Boolean AND search for terms: {query_terms}")

        term_postings = {}  # Store postings so we don't call get_postings() multiple times
        for term in query_terms:
            term_postings[term] = self.get_postings(term)

        # Get postings dynamically from disk
        posting_list = [set(term_postings[term].keys()) for term in query_terms]

        if not posting_list or any(len(postings) == 0 for postings in posting_list):
            self.printd("DEBUG: At least one term has no postings, returning empty results.")
            return []

        common_docs = set.intersection(*posting_list) if posting_list else set()

        if not common_docs:
            self.printd("DEBUG: No common documents found among terms!")
            return []

        self.printd(f"DEBUG: Found {len(common_docs)} documents containing all query terms.")

        # Compute TF-IDF ranking
        doc_vectors = {}
        query_vector = np.array([1] * len(query_terms))  # Binary query vector

        for doc_id in common_docs:
            doc_vectors[doc_id] = np.array([
                term_postings[term].get(doc_id, {}).get("tf-idf", 0) for term in query_terms
            ])

        ranked_results = sorted(
            common_docs,
            key=lambda doc: np.dot(doc_vectors[doc], query_vector) /
            (np.linalg.norm(doc_vectors[doc]) * np.linalg.norm(query_vector) + 1e-9),
            reverse=True
        )

        self.printd(f"DEBUG: Ranked {len(ranked_results)} documents based on TF-IDF score.")
        return ranked_results

    def search(self, query):
        """Performs a search and returns the top 5 document URLs."""
        start_time = time.perf_counter()
        results = self.boolean_and_search(query)
        elapsed_time = time.perf_counter() - start_time

        if not results:
            print(f"No results found. (Query time: {elapsed_time:.6f} seconds)")
            return

        print(f"Query time: {elapsed_time:.6f} seconds")
        for rank, doc_id in enumerate(results[:5], 1):
            print(f"{rank}. {doc_id}")
        

    def generate_report(self):
        """Generates a PDF report for predefined queries."""
        self.boolean_and_search('test') # ensures subsequent queries are constant time
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

        for query in queries:
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(200, 10, f"Query: {query}", ln=True)
            start_time = time.perf_counter()
            results = self.boolean_and_search(query)
            elapsed_time = time.perf_counter() - start_time

            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, f"Elapsed time: {elapsed_time:.6f} seconds", ln=True)
            pdf.ln(5)

            if not results:
                pdf.cell(200, 10, "No results found.", ln=True)
            else:
                for rank, doc_id in enumerate(results[:5], 1):
                    pdf.cell(200, 10, f"{rank}. {doc_id}", ln=True)

            pdf.ln(10)

        pdf.output("search_report.pdf")
        print("Report saved as 'search_report.pdf'!")
        

if __name__ == "__main__":
    search_engine = SearchEngine("partial_index/final_index.jsonl")  # Use JSONL format

    choice = input("\nWould you like to run the searcher or generate the report? (run/report): ").strip().lower()

    if choice == "report":
        search_engine.generate_report()
    elif choice == "run":
        while True:
            query = input("\nEnter your search query (or type 'exit' to quit): ").strip()
            if query.lower() == "exit":
                print("Exiting search.")
                break
            search_engine.search(query)

    search_engine.close()
