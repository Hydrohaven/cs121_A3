import os
import json
import glob
import re
import shutil
from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
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

        self.input_dir = input_dir # Directory to open and process
        self.index_dir = index_dir
        self.chunk_size = chunk_size # Chunk size on what we are looping, avoiding using too much memory
        self.report_file = report_file
        self.inverted_index = defaultdict(lambda: defaultdict(int))  # {term: {doc_id: frequency}}
        self.stemmer = PorterStemmer()
        self.doc_count = 0
        self.partial_index_count = 0
        self.doc_urls = {}  # {doc_id: URL}

        if not os.path.exists(index_dir):
            os.makedirs(index_dir)

    def get_all_json_files(self):
        """Recursively finds all JSON files inside the nested directories."""
        return glob.glob(os.path.join(self.input_dir, '**', '*.json'), recursive=True)

    def process_files(self):
        """Processes all JSON files, extracts terms, and builds the inverted index."""
        pass

    def extract_tokens(self, html_content):
        """Extracts important text from HTML, tokenizes and stems words."""
        soup = BeautifulSoup(html_content, 'html.parser')
        important_text = []

        if soup.title:
            important_text.append(soup.title.text)
        for tag in soup.find_all(["h1", "h2", "h3", "b", "strong"]):
            important_text.append(tag.text)

        tokens = []
        for text in important_text:
            words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())  # Extract alphanumeric words
            tokens.extend([self.stemmer.stem(word) for word in words])  # Stem words

        return tokens

    def write_partial_index(self):
        """Writes a partial inverted index to disk and clears memory."""

    def merge_indexes(self):
        """Merges all partial indexes into a final inverted index."""
        pass

    def generate_report(self):
        """Generates a PDF report with stats: # of documents, unique tokens, total index size, and partial index count."""
        pass

# RUN WHEN EVERYTHING IS MADE!
if __name__ == "__main__":
    input_directory = "developer"
    output_directory = "partial"

    indexer = InvertedIndexer(input_directory, output_directory)
    indexer.process_files()  # Build inverted index
    indexer.merge_indexes()  # Merge partial indexes
    indexer.generate_report()  # Generate the required report