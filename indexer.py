import os
import json
import glob
import re
import shutil
import math
import numpy as np
from collections import defaultdict
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from fpdf import FPDF

class InvertedIndexer:
    def __init__(self, input_dir, index_dir, chunk_size=500, report_file="index_report.pdf"):
        """
        Initializes the indexer.

        - input_dir: Directory containing website folders with JSON files.
        - index_dir: Directory to store inverted index files.
        - chunk_size: Number of documents processed before writing a partial index.
        - report_file: Path for the generated report (PDF).
        """
        nltk.download("wordnet")
        nltk.download("omw-1.4")

        self.input_dir = input_dir # Directory to open and process
        self.index_dir = index_dir
        self.chunk_size = chunk_size # Chunk size on what we are looping, avoiding using too much memory
        self.report_file = report_file

        # Now stores both TF and TF-IDF
        self.inverted_index = defaultdict(lambda: defaultdict(lambda: {"tf": 0, "tf-idf": 0}))
        self.lemmatizer = WordNetLemmatizer() # much better than stemmer, ensures real english words 
        self.doc_count = 0
        self.partial_index_count = 0
        self.doc_urls = {}  
        self.document_frequencies = defaultdict(int)  # Tracks number of documents each term appears in
        self.simhashes = {}

        if not os.path.exists(index_dir):
            os.makedirs(index_dir)


    def get_all_json_files(self):
        """Recursively finds all JSON files inside the nested directories."""
        return glob.glob(os.path.join(self.input_dir, '**', '*.json'), recursive=True)
    

    def process_files(self):
        """Processes all JSON files, extracts terms, and builds the inverted index."""

        # If self.index_dir already exists, it delete it completely and creates a new empty directory to store new index
        if os.path.exists(self.index_dir):
            shutil.rmtree(self.index_dir)  # Deletes old index folder
            os.makedirs(self.index_dir)  # Recreates a fresh directory

        # Gets list of all JSON files that need to be processed
        file_list = self.get_all_json_files()

        # Loops over each JSON file and then opens and loads JSON file into data
        for file_path in file_list:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            url = data.get("url", file_path)  # Use URL or filename as document ID
            html_content = data.get("content", "") # Retrieves the HTML content of the webpage

            # Extracts tokens from the HTML Content
            tokens = self.extract_tokens(html_content)

            unique_terms = set()  # Track unique terms in the document
            for token in tokens:
                self.inverted_index[token][url]["tf"] += 1  
                unique_terms.add(token)  

            for term in unique_terms:
                self.document_frequencies[term] += 1  

            self.doc_urls[url] = url
            self.doc_count += 1

            # Write partial index every N documents
            if self.doc_count % self.chunk_size == 0:
                self.write_partial_index()

        # Write any remaining data
        if self.inverted_index:
            self.write_partial_index()

    def extract_tokens(self, html_content):
        """Extracts important text from HTML, tokenizes and stems words."""
        soup = BeautifulSoup(html_content, 'html.parser')
        important_text = []

        if soup.title: # extract title
            important_text.append(soup.title.text) 
        for tag in soup.find_all(["h1", "h2", "h3", "b", "strong"]): # extracts headers and bold text
            important_text.append(tag.text)

        # extracts normal words
        body_text = soup.get_text()
        tokens = []

        for text in important_text + [body_text]:
            words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())  # Extract alphanumeric words
            lemmatized_words = [self.lemmatizer.lemmatize(word) for word in words]  # Apply lemmatization
            tokens.extend(lemmatized_words)

        return tokens

    def write_partial_index(self):
        """Writes a partial inverted index to disk using JSONL format."""
        
        if not self.inverted_index:
            return  # Don't write an empty index
        
        partial_index_path = os.path.join(self.index_dir, f"partial_index_{self.partial_index_count}.jsonl")

        with open(partial_index_path, 'w', encoding='utf-8') as f:
            for term, postings in self.inverted_index.items():
                json_line = json.dumps({term: postings})  # Convert each term to a JSON object
                f.write(json_line + "\n")  # Write as a line in the file
        
        print(f"Saved partial index: {partial_index_path}")

        self.inverted_index.clear()  # Clear memory after saving
        self.partial_index_count += 1


    def compute_tf_idf(self):
        """Computes TF-IDF scores for each term in the index."""
        total_documents = self.doc_count  

        for term, postings in self.inverted_index.items():
            df = self.document_frequencies[term]  
            idf = math.log10(total_documents / df) if df > 0 else 0  

            for doc_id, data in postings.items():
                tf = 1 + math.log10(data["tf"]) if data["tf"] > 0 else 0  
                self.inverted_index[term][doc_id]["tf-idf"] = tf * idf  

    def merge_indexes(self):
        """Merges all partial indexes into a final inverted index and computes TF-IDF."""
        final_index_path = os.path.join(self.index_dir, "final_index.jsonl")  # Use .jsonl format

        partial_files = glob.glob(os.path.join(self.index_dir, "partial_index_*.jsonl"))
        
        final_index = defaultdict(lambda: defaultdict(lambda: {"tf": 0, "tf-idf": 0}))

        for file in partial_files:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:  # Read line-by-line
                    try:
                        entry = json.loads(line.strip())  # Parse each line as JSON
                        term, postings = next(iter(entry.items()))
                        
                        for doc_id, data in postings.items():
                            final_index[term][doc_id]["tf"] += data["tf"]

                    except json.JSONDecodeError:
                        print(f"Skipping malformed JSON line in {file}")

        self.inverted_index = final_index
        self.compute_tf_idf()  

        # Write final index in JSONL format
        with open(final_index_path, 'w', encoding='utf-8') as f:
            for term, postings in self.inverted_index.items():
                json_line = json.dumps({term: postings})
                f.write(json_line + "\n")

        print(f"Merged index saved: {final_index_path}")


    def generate_report(self):
        """Generates a PDF report with indexing stats."""
        if os.path.exists(self.report_file):
            os.remove(self.report_file)

        # Load the final index file
        final_index_path = os.path.join(self.index_dir, "final_index.json")
        if not os.path.exists(final_index_path):
            print("Error: Final index file not found. Run `merge_indexes()` first.")
            return
        
        with open(final_index_path, 'r', encoding='utf-8') as f:
            final_index = json.load(f)

        num_docs = self.doc_count  # Total number of documents processed
        num_unique_tokens = len(final_index)  # Unique terms count
        total_index_size_kb = sum(os.path.getsize(f) for f in glob.glob(os.path.join(self.index_dir, "*.json"))) / 1024
        num_partial_indexes = len(glob.glob(os.path.join(self.index_dir, "partial_index_*.json")))  # Count of partial indexes

        # Create PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, "Inverted Index Report", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, f"Total Documents Indexed: {num_docs}", ln=True)
        pdf.cell(200, 10, f"Unique Words in Index: {num_unique_tokens}", ln=True)
        pdf.cell(200, 10, f"Total Index Size on Disk: {total_index_size_kb:.2f} KB", ln=True)
        pdf.cell(200, 10, f"Number of Partial Indexes: {num_partial_indexes}", ln=True)

        # Save the PDF report
        pdf.output(self.report_file)
        print(f"Report saved to: {self.report_file}")

if __name__ == "__main__":
    input_directory = "developer"
    output_directory = "hash_test"

    indexer = InvertedIndexer(input_directory, output_directory)
    indexer.process_files()  # Build inverted index
    indexer.merge_indexes()  # Merge partial indexes
    indexer.generate_report()  # Generate the required report