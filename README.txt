CS121 A3: Inverted Index
Created by Joshua Sullivan (20577887), Margaret Galvez (21978491), and Nathan Ong (76719148)

Setup
### Step 1: Create Python Virtual Environment
```
python -m venv env
```

### Step 2: Activate Virtual Environment
```
env/Scripts/activate
```
or relaunch VSCode Terminal (VSCode automatically activates venvs)

### Step 3: Install Dependencies
```
pip install -r requirements.txt
```

### Step 4: Run Indexer (takes a while to load everything!)
```
py indexer.py
```
make sure you have all the necessary files professor gave us in a directory called 'developer', won't work otherwise. 
Ensure 'final_index.jsonl' is in a directory titled 'partial_index'.

### Step 5: Run Search Engine (Web GUI)
```
uvicorn app:app --reload
```

### Step 6: Querying the Search Engine
Type into the input box and click search to display the top 50 results of that given query.

*Note: The first query will always take 2-3 seconds due to offset loading to ensure subsequent queries are always O(1)
