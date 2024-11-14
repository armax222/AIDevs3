# Standard library imports
import requests
import re

# Third-party imports
from bs4 import BeautifulSoup
from utilities.common import OpenAIClient
from utilities.config import S01E01_TASK_URL, S01E01_TASK_USERNAME, S01E01_TASK_PASSWORD

# Configuration 
url, username, password = S01E01_TASK_URL, S01E01_TASK_USERNAME, S01E01_TASK_PASSWORD

# Initialize OpenAI client
client_openai = OpenAIClient()

def get_current_question():
    """Fetches the current question from the specified URL using BeautifulSoup."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        question_tag = soup.find('p', id='human-question')
        return question_tag.get_text().strip() if question_tag else None
    except requests.RequestException as err:
        print(f"Error: {err}")
        return None

def extract_flag(html_content):
    """Simplified flag extraction using BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')
    # Find any text containing the pattern {FLG:...}
    flag_text = soup.find(string=lambda text: text and "{FLG:" in text)
    return flag_text.split("{FLG:")[1].split("}")[0].strip() if flag_text else None

def main():
    # Fetch question and get AI-generated answer using ChatML format
    question = get_current_question()
    if question:
        # Define the ChatML messages structure for clarity and accuracy
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions with numbers only. Return only the number as your answer."},
            {"role": "user", "content": question}
        ]

        # Get completion from the OpenAI client using the ChatML format messages
        answer = client_openai.get_completion(messages=messages, model="gpt-4o-mini", temperature=0.1)
        print(question, " Answer:", answer)

        # Submit login data and retrieve flag if available
        response = requests.post(
            url,
            data={'username': username, 'password': password, 'answer': answer}
        )
        if response.status_code == 200:
            # Use simplified BeautifulSoup extraction for the flag
            flag = extract_flag(response.text)
            print("{FLG:} found:", flag if flag else "No flag found.")
        else:
            print(f"Login failed. Status: {response.status_code}")
    else:
        print("Failed to retrieve the question.")

if __name__ == "__main__":
    main()