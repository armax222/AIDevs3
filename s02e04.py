from utilities.common import AIDevsClient, OpenAIClient
from utilities.config import AI_DEVS_API_KEY, S02E04_TASK_URL, S02E04_REPORT_URL
import requests
import zipfile
import os
import base64
import shutil

# =========================================================
# Configuration
# =========================================================
TASK_NAME = "kategorie"
ZIP_URL = S02E04_TASK_URL
ZIP_PATH = "s02e04/pliki_z_fabryki.zip"
EXTRACT_FOLDER = "s02e04/files"
SUBMIT_URL = S02E04_REPORT_URL

# Initialize clients
client_aidevs = AIDevsClient()
client_openai = OpenAIClient()

# =========================================================
# Step 2: Helper functions
# =========================================================
def get_file_content(file_path):
    """Retrieve file content based on type."""
    try:
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_path.endswith(('.mp3', '.wav')):
            return client_openai.transcribe(file_path).get('text', '') 
        elif file_path.endswith('.png'):
            encoded_data = base64.b64encode(open(file_path, "rb").read()).decode('utf-8')
            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Czy ten obraz zawiera informacje o ludziach, którzy zostali schwytani i są gdzieś przetrzymywani czy o naprawionych usterkach hardwarowych (wyklucz aktualizacje modułu AI)? Opisz w szczegółach."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_data}"}}
                ]
            }]
            return client_openai.get_completion(messages=messages, model="gpt-4o", temperature=0.1)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return ''

def categorize_content(content):
    print(content)
    """Categorize content into 'people', 'hardware', or 'none'."""
    messages = [{
        "role": "system",
        "content": """"Klasyfikuj:
            1. 'people' - notatki zawierające informacje o poszukiwanych ludziach, którzy zostali schwytani i są gdzieś przetrzymywani.
            2. 'hardware' - notatki o naprawionych usterkach hardwarowych.
            W pozostałych przypadkach odpowiedz 'none'.
            Odpowiedz jednym słowem: 'people', 'hardware' or 'none'."""
    }, {
        "role": "user",
        "content": f"Categorize this content: {content}"
    }]
    
    category = client_openai.get_completion(
        messages=messages,
        model="gpt-4o",
        temperature=0.1
    ).strip().lower()
    
    return category if category in ['people', 'hardware'] else None

def main():
    # =========================================================
    # Step 1: Clean and prepare directories
    # =========================================================
    if os.path.exists(os.path.dirname(ZIP_PATH)):
        shutil.rmtree(os.path.dirname(ZIP_PATH))

    os.makedirs(os.path.dirname(ZIP_PATH), exist_ok=True)
    os.makedirs(EXTRACT_FOLDER, exist_ok=True)

    # Download and extract ZIP file
    response = requests.get(ZIP_URL)
    if response.status_code == 200:
        with open(ZIP_PATH, "wb") as file:
            file.write(response.content)
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_FOLDER)
    else:
        print("Failed to download the ZIP file.")
        exit(1)

    # =========================================================
    # Step 3: Process files and categorize
    # =========================================================
    categories = {"people": [], "hardware": []}

    for root, _, files in os.walk(EXTRACT_FOLDER):
        if "facts" not in root:
            for file in sorted(files):
                print(file)
                content = get_file_content(os.path.join(root, file))
                if content:
                    category = categorize_content(content)
                    print(category)
                    if category and category != 'none':
                        categories[category].append(file)

    categories = {k: sorted(v) for k, v in categories.items()}
    print(categories)

    # =========================================================
    # Step 4: Submit answer
    # =========================================================
    payload = {
        "task": TASK_NAME,
        "apikey": AI_DEVS_API_KEY,
        "answer": categories
    }

    response = client_aidevs.submit_answer(
        answer=payload, 
        submit_url=SUBMIT_URL
    )

    print(f"Submission response: {response}")

if __name__ == "__main__":
    main()