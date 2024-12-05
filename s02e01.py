import os
import requests
import zipfile
from utilities.common import OpenAIClient, AIDevsClient
from utilities.config import AI_DEVS_API_KEY, S02E01_TASK_URL, S02E01_REPORT_URL

# Configuration
ZIP_URL = S02E01_TASK_URL
ZIP_PATH = "przesluchania.zip"
AUDIO_FOLDER = "audio_files"
OUTPUT_FILE_PATH = "transcripts.txt"
TASK_NAME = "mp3"
SUBMIT_URL = S02E01_REPORT_URL

# Step 1: Download and extract the ZIP file containing audio
response = requests.get(ZIP_URL)
if response.status_code == 200:
    with open(ZIP_PATH, "wb") as file:
        file.write(response.content)
    print("ZIP file downloaded successfully.")

    os.makedirs(AUDIO_FOLDER, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(AUDIO_FOLDER)
    print(f"Files extracted to folder: {AUDIO_FOLDER}")
else:
    print("Failed to download the ZIP file.")
    exit(1)

# Step 2: Transcribe audio files using OpenAIClient
client_openai = OpenAIClient()
transcripts = {}

for audio_file in os.listdir(AUDIO_FOLDER):
    if audio_file.endswith(('.mp3', '.wav', '.m4a')):
        audio_path = os.path.join(AUDIO_FOLDER, audio_file)
        print(f"Processing file: {audio_file}")
        audio_response = client_openai.transcribe(audio_path)
        if audio_response and "text" in audio_response:
            transcripts[audio_file] = audio_response["text"]
            print(f"Transcription for {audio_file}: {audio_response['text']}")
        else:
            print(f"Error processing {audio_file}.")

# Step 3: Write transcripts to a file
with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as output_file:
    for audio_file, transcript in transcripts.items():
        output_file.write(f"Transcription for {audio_file}:\n{transcript}\n\n")
print(f"Transcripts have been written to {OUTPUT_FILE_PATH}.")

# Step 4: Read transcripts back from file and combine
final_transcripts = {}
with open(OUTPUT_FILE_PATH, "r", encoding="utf-8") as input_file:
    current_file = None
    current_transcript_lines = []

    for line in input_file:
        if line.startswith("Transcription for "):
            if current_file and current_transcript_lines:
                final_transcripts[current_file] = "".join(current_transcript_lines).strip()
            current_file = line.split("Transcription for ")[1].strip().rstrip(":")
            current_transcript_lines = []
        else:
            current_transcript_lines.append(line)

    if current_file and current_transcript_lines:
        final_transcripts[current_file] = "".join(current_transcript_lines).strip()

print(f"Transcripts have been read from {OUTPUT_FILE_PATH}.")

# Combine all transcripts into a single string
combined_transcript = "\n".join(final_transcripts.values())

# Step 5: Define the system and user prompts
messages = [
    {
        "role": "system",
        "content": (
            "Jesteś doświadczonym detektywem z wieloletnim stażem, specjalizującym się w analizowaniu niejasnych i często sprzecznych zeznań. "
            "Twoim celem jest ustalenie nazwy ulicy, przy której znajduje się instytut, w którym wykłada profesor Andrzej Maj, na podstawie załączonych zeznań świadków.\n\n"
            "Wskazówki:\n"
            "- Dokładnie przeanalizuj każde zeznanie, biorąc pod uwagę, że mogą w nich wystąpić kłamstwa, przeinaczenia faktów lub informacje nieistotne.\n"
            "- Zwracaj uwagę na szczegóły, które pomogą Ci powiązać zeznania w spójną całość.\n"
            "- Rozważ swoją wiedzę ogólną lub potencjalne skojarzenia, które mogą wyniknąć z poszlak zawartych w zeznaniach.\n"
            "- Nie śpiesz się. Omów swój tok rozumowania krok po kroku, a następnie sformułuj ostateczną odpowiedź.\n\n"
            "Oto zeznania świadków:\n" + combined_transcript
        )
    },
    {
        "role": "user",
        "content": "Podaj proszę nazwę ulicy, na której znajduje się uczelnia (konkretny instytut!), gdzie wykłada profesor Andrzej Maj."
    }
]

# Step 6: Use the OpenAIClient to analyze the transcripts
street = client_openai.get_completion(messages=messages, model="gpt-4o", temperature=0.1, max_tokens=700)
print("Analysis Result:")
print(street)

# Step 7: Submit the answer
client_aidevs = AIDevsClient()
street_name = street.strip()

payload = {
    "task": TASK_NAME,
    "apikey": AI_DEVS_API_KEY,
    "answer": street_name
}

submission_response = client_aidevs.submit_answer(answer=payload, submit_url=SUBMIT_URL)

if submission_response:
    print("Answer submitted successfully!")
    print(f"Response: {submission_response}")
else:
    print("Failed to submit the answer.")