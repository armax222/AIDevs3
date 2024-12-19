# Standard library imports
import glob
import os
import re
import shutil
import zipfile

# Third-party imports
import chromadb
import requests

# Local imports
from utilities.common import AIDevsClient, OpenAIClient
from utilities.config import AI_DEVS_API_KEY, S03E02_TASK_URL, S03E02_REPORT_URL

# Configuration constants
TASK_NAME = "wektory"
SUBMIT_URL = S03E02_REPORT_URL
ZIP_URL = S03E02_TASK_URL
MAIN_ZIP_PATH = "s03e02/pliki_z_fabryki.zip"
WEAPONS_ZIP_PATH = "s03e02/files/weapons_tests.zip"
EXTRACT_FOLDER = "s03e02/files"
WEAPONS_EXTRACT_FOLDER = "s03e02/weapons"
WEAPONS_FOLDER = "s03e02/weapons/do-not-share"
ZIP_PASSWORD = "1670"

def setup_directories():
    """Clean and prepare directories."""
    if os.path.exists(os.path.dirname(MAIN_ZIP_PATH)):
        shutil.rmtree(os.path.dirname(MAIN_ZIP_PATH))
    
    os.makedirs(os.path.dirname(MAIN_ZIP_PATH), exist_ok=True)
    os.makedirs(EXTRACT_FOLDER, exist_ok=True)
    os.makedirs(WEAPONS_EXTRACT_FOLDER, exist_ok=True)

def download_and_extract_files():
    """Download and extract ZIP files."""
    response = requests.get(ZIP_URL)
    if response.status_code != 200:
        print("Failed to download the ZIP file.")
        return False
        
    with open(MAIN_ZIP_PATH, "wb") as file:
        file.write(response.content)
    with zipfile.ZipFile(MAIN_ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_FOLDER)
        
    with zipfile.ZipFile(WEAPONS_ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(path=WEAPONS_EXTRACT_FOLDER, pwd=ZIP_PASSWORD.encode())
    
    return True

def extract_date_from_filename(filename: str) -> str:
    """Extract date from filename in YYYY_MM_DD format."""
    date_pattern = r'(\d{4}_\d{2}_\d{2})'
    match = re.search(date_pattern, filename)
    return match.group(1).replace("_", "-") if match else None

def get_file_content(file_path: str) -> str:
    """Extract content from text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return ''

def process_file(file_path, client_openai):
    """Process a single file and return its date, content, and embedding."""
    date = extract_date_from_filename(file_path)
    content = get_file_content(file_path)
    embedding = client_openai.create_embeddings(content)
    return date, content, embedding

def setup_chroma_collection():
    """Initialize and setup ChromaDB collection."""
    chroma_client = chromadb.Client()
    try:
        chroma_client.delete_collection(name="weapons_reports")
    except:
        pass
    return chroma_client.create_collection(
        name="weapons_reports",
        metadata={"hnsw:space": "cosine"},
        embedding_function=None
    )

def process_and_add_files(collection, client_openai):
    """Process all files and add them to the Chroma collection."""
    for file_path in glob.glob(os.path.join(WEAPONS_FOLDER, '*.txt')):
        date, content, embedding = process_file(file_path, client_openai)
        if content and embedding:
            collection.add(
                documents=[content],
                metadatas=[{"date": date}],
                ids=[os.path.basename(file_path)],
                embeddings=[embedding]
            )
            print(f"Added file: {file_path} with date {date}")

def main():
    # Initialize clients
    client_aidevs = AIDevsClient()
    client_openai = OpenAIClient()
    
    # Setup and extract files
    setup_directories()
    if not download_and_extract_files():
        return
    
    # Setup and process ChromaDB
    collection = setup_chroma_collection()
    process_and_add_files(collection, client_openai)
    
    # Generate and execute query
    query = "Wzmianka o kradzieży prototypu broni"
    query_embedding = client_openai.create_embeddings(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1
    )
    
    # Submit answer
    response = client_aidevs.submit_answer(
        answer={"task": TASK_NAME, "apikey": AI_DEVS_API_KEY, "answer": results['metadatas'][0][0]['date']},
        submit_url=SUBMIT_URL
    )
    
    print(response) 

if __name__ == "__main__":
    main()