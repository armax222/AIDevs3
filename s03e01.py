import base64
import os
import requests
import zipfile
import shutil
from utilities.common import AIDevsClient, OpenAIClient
from utilities.config import AI_DEVS_API_KEY, S03E01_TASK_URL, S03E01_REPORT_URL

# =========================================================
# Configuration
# =========================================================
TASK_NAME = "dokumenty"
ZIP_URL = S03E01_TASK_URL
ZIP_PATH = "s03e01/pliki_z_fabryki.zip"
EXTRACT_FOLDER = "s03e01/files"
SUBMIT_URL = S03E01_REPORT_URL

def read_file_content(path):
    """Read content from a file or directory of files.
    Supports: single files (txt/mp3/wav/png) or directories containing txt files."""
    try:
        # Handle directory
        if os.path.isdir(path):
            content = []
            for root, _, files in os.walk(path):
                for f in files:
                    file_path = os.path.join(root, f)
                    file_content = read_file_content(file_path)
                    print(file_path, file_content)
                    if file_content:
                        content.append(file_path + ": " + file_content)
            return "\n\n".join(content)
        
        # Handle single files
        if path.endswith('.txt'):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        
        if path.endswith(('.mp3', '.wav')):
            return client_openai.transcribe(path).get('text', '')
        
        if path.endswith('.png'):
            encoded = base64.b64encode(open(path, "rb").read()).decode('utf-8')
            return client_openai.get_completion(
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Dokładnie opisz wszystkie detale obrazka. Odczytaj wszystkie teksty i elementy graficzne."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded}"}}
                    ]
                }],
                model="gpt-4o-mini",
                temperature=0.1
            )
            
    except Exception as e:
        print(f"Error processing {path}: {e}")
        return ''

def generate_keywords(content, facts_summary, client_openai):
    """Generate keywords for a given content using GPT."""
    messages = [
        {
            "role": "system",
            "content": (
                "Jesteś ekspertem w generowaniu słów kluczowych dla dokumentów. "
                "Twoim zadaniem jest wygenerowanie listy 50 słów kluczowych w języku polskim, "
                "które najlepiej opisują treść dokumentu w kontekście podanych informacji. "
                "Słowa kluczowe muszą spełniać następujące kryteria: "
                "- Być w mianowniku liczby pojedynczej. "
                "- Ściśle powiązane z treścią dokumentu i kontekstem. "
                "Make sure that the generated keywords include all the most important information from the content."
                "Think step-by-step about the content to make sure you have all the information and take your time."
                "Zwróć wyłącznie listę słów kluczowych oddzielonych przecinkami, bez dodatkowych wyjaśnień."
            )
        },
        {
            "role": "user",
            "content": (
                "Przeanalizuj poniższy dokument w kontekście podanych faktów "
                "i wygeneruj słowa kluczowe, które łączą się z szerszym kontekstem, "
                "szczególnie uwzględniając wykonywane dawniej zawody, znane języki programowania i sektor gdzie znaleziono ich ślady.\n\n"
                
                "Dokument:\n"
                f"{content}\n\n"
                "Kontekst:\n"
                f"{facts_summary}"
            )
        }
    ]
    
    return client_openai.get_completion(
        messages=messages,
        model="gpt-4o-mini",  
        temperature=0.1
    ).strip()

def main():
    # Initialize clients
    client_aidevs = AIDevsClient()
    client_openai = OpenAIClient()

    # Clean and prepare directories
    if os.path.exists(os.path.dirname(ZIP_PATH)):
        shutil.rmtree(os.path.dirname(ZIP_PATH))

    os.makedirs(os.path.dirname(ZIP_PATH), exist_ok=True)
    os.makedirs(EXTRACT_FOLDER, exist_ok=True)

    # Download and extract ZIP file
    response = requests.get(ZIP_URL)
    if response.status_code != 200:
        print("Failed to download the ZIP file.")
        return

    with open(ZIP_PATH, "wb") as file:
        file.write(response.content)
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_FOLDER)

    # Process files
    facts = read_file_content("s03e01")
    
    # Summarize facts
    facts_summary = client_openai.get_completion(
        messages=[{
            "role": "user",
            "content": f"Summarize the following information about indyviduals, their profesions, known programming languages and if trace of them is found, describe it in detail and extract exact name of sector (A1-C4): {facts}"
                        "Think step-by-step about the content to make sure you have all the information."
        }],
        model="gpt-4o-mini",
        temperature=0.1
    )

    print(facts_summary)

    # Generate keywords for each file
    keywords_dict = {}
    for file in sorted(os.listdir(EXTRACT_FOLDER)):
        if file.endswith('.txt') and not os.path.join(EXTRACT_FOLDER, file).startswith(os.path.join(EXTRACT_FOLDER, "facts")):
            print(f"Processing {file}...")
            content = read_file_content(os.path.join(EXTRACT_FOLDER, file))
            keywords = generate_keywords(content, facts_summary, client_openai)
            keywords_dict[file] = keywords

    print("Generated keywords:", keywords_dict)

    # Submit answer
    payload = {
        "task": TASK_NAME,
        "apikey": AI_DEVS_API_KEY,
        "answer": keywords_dict
    }

    response = client_aidevs.submit_answer(
        answer=payload,
        submit_url=SUBMIT_URL
    )

    print(f"Submission response: {response}")

if __name__ == "__main__":
    main()