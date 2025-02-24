# No Lucene PyLucene or ElasticSearch

import re
import json
import os
import math
import lxml
from bs4 import BeautifulSoup
from collections import defaultdict
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize


# Inverted Indexer
class Indexer():
    # Step 0: Initialize Class
    def __init__(self) -> None:
        self.dev_directory = r"./developer"  # JSON files directory
        self.document_id = 0
        self.inverted_index = defaultdict(list)  # inverted_index = {key: token, value: document_id, freq, importance, tf_idf}
        self.url_map = {}  # url_map = {key: document_id, value: url
        self.processed_hashes = (set())  # Store the hash of pages; detect and eliminate duplicate pages.
        self.word_stemmer = PorterStemmer()  # Create an instance of PorterStemmer
        self.inv_index_location = defaultdict(int)  # allow the usage of seek() when searching word

    # Step 1: Initialize a Dictionary that will contain tokens and its respective list of postings

        # List of Postings: Each document is represented by let's say for now a number. Each posting represents
        #                   the number that the token appears in.

    def open_json_files():
        dev_folder = '/developer' # Developer folder path
        for json_file in dev_folder.rglob("*.json"):
            with json_file.open("r") as file:
                print(json_file)
                break

    # Step 2: Create tokens from the HTML? files. Read over JSONs and identify tokens.

    # Step 3: While looping over JSON files for token, add their respective document it appears to the Posting List

    # Step 4: Print number of indexed documents (Should be 55,393)

    # Step 5: Print the number of unique words you found

    # Step 6: Total Size of Index (KB) in the disk 

def main():
    indexer_obj = Indexer()
    indexer_obj.open_json_files()
    