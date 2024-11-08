# Standard library imports
import requests
import re

# Third-party imports
from utilities.common import OpenAIClient
from utilities.config import S01E01_TASK_URL, S01E01_TASK_USERNAME, S01E01_TASK_PASSWORD

# Configuration 
url, username, password = S01E01_TASK_URL, S01E01_TASK_USERNAME, S01E01_TASK_PASSWORD

# Initialize OpenAI client
client_openai = OpenAIClient()

def get_current_question():
    """Fetches the current question from the specified URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        match = re.search(r'<p id="human-question">(.*?)</p>', response.text)
        return match.group(1).strip() if match else None
    except requests.RequestException as err:
        print(f"Error: {err}")
        return None

def main():
    # Fetch question and get AI-generated answer
    question = get_current_question()
    if question:
        answer = client_openai.get_completion(
            prompt=f"Answer just numbers: {question}", temperature=0.1
        )
        print(question, " Answer:", answer)

        # Submit login data and retrieve flag if available
        response = requests.post(
            url,
            data={'username': username, 'password': password, 'answer': answer}
        )
        if response.status_code == 200:
            match = re.search(r"\{FLG:(.*?)\}", response.text)
            print("{FLG:} found:", match.group(1).strip() if match else "No flag found.")
        else:
            print(f"Login failed. Status: {response.status_code}")
    else:
        print("Failed to retrieve the question.")

if __name__ == "__main__":
    main()