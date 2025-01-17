# Standard library imports
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

# Local imports
from utilities.common import AIDevsClient, OpenAIClient
from utilities.config import AI_DEVS_API_KEY, S04E03_TASK_URL, S04E03_REPORT_URL, S04E03_WWW_URL

# =========================================================
# Configuration
# =========================================================
TASK_NAME = "softo"
BASE_URL = "https://softo.ag3nts.org"
QUESTIONS_URL = S04E03_TASK_URL + AI_DEVS_API_KEY + "/softo.json"
SUBMIT_URL = S04E03_REPORT_URL

# Initialize clients
client_aidevs = AIDevsClient()
client_openai = OpenAIClient()

# =========================================================
# Helper Functions
# =========================================================
def get_questions():
    """Fetch questions from the central server."""
    try:
        response = requests.get(QUESTIONS_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching questions: {e}")
        return None

def get_page_content(url):
    """Fetch and parse webpage content."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching page {url}: {e}")
        return None

def analyze_page(soup, question):
    """Use LLM to analyze page content and determine if it contains the answer."""
    text_content = soup.get_text(strip=True)
    links = soup.find_all('a')
    link_texts = [
        f"{link.get_text(strip=True)} ({urljoin(BASE_URL, link.get('href'))})"
        for link in links if link.get('href')
    ]

    system_content = (
        "You are an AI assistant helping to find answers to specific questions on webpages. "
        "If you find a direct answer to the question, return it prefixed with 'ANSWER: '. "
        "If no answer is directly found, analyze all available links and suggest the best one to explore further, prefixed with 'FOLLOW_LINK: ', nothing more. "
        "If question is about the link, return the link prefixed with 'ANSWER: '. "
        "If no relevant information or link is found, return 'NOT_FOUND'. "
        "Be very precise and concise."
    )
    
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": f"Question: {question}\n\nPage content: {text_content}\n\nLinks:\n{chr(10).join(link_texts)}"}
    ]
    
    result = client_openai.get_completion(
        messages=messages,
        model="gpt-4o",
        temperature=0.1
    )

    print(f"Result: {result}")
    
    cleaned_result = re.sub(r'\[.*?\]\((.*?)\)', r'\1', result.strip())
    return cleaned_result

def find_answer(question, max_depth=7):
    """Search for answer to a question with depth limit."""
    visited = set()
    current_url = BASE_URL
    depth = 0
    
    while depth < max_depth:
        if current_url in visited:
            return None
            
        print(f"\nVisiting: {current_url}")
        visited.add(current_url)
        
        soup = get_page_content(current_url)
        if not soup:
            return None
            
        result = analyze_page(soup, question)
        
        if result.startswith('ANSWER:'):
            return result.replace('ANSWER:', '').strip()
            
        if result.startswith('FOLLOW_LINK:'):
            next_url = result.replace('FOLLOW_LINK:', '').strip()
            if next_url and next_url not in visited:
                current_url = next_url
                depth += 1
                continue
        
        links = soup.find_all('a')
        for link in links:
            href = link.get('href')
            if href:
                next_url = urljoin(BASE_URL, href)
                if next_url not in visited:
                    current_url = next_url
                    depth += 1
                    break
        else:
            return None
        
    return None

def main():
    """Main execution function."""
    # Step 1: Get questions
    questions = get_questions()
    if not questions:
        print("Failed to get questions")
        return

    print("Successfully fetched questions:", questions)

    # Step 2: Process questions and find answers
    answers = {}
    for q_id, question in questions.items():
        print(f"Processing question: {q_id}")
        answer = find_answer(questions[q_id])
        if answer:
            answers[q_id] = answer

    print("Found answers:", answers)

    # Step 3: Submit answers
    if answers:
        payload = {
            "task": TASK_NAME,
            "apikey": AI_DEVS_API_KEY,
            "answer": answers
        }
        
        response = client_aidevs.submit_answer(
            answer=payload,
            submit_url=SUBMIT_URL
        )
        print(f"\nSubmission response: {response}")
    else:
        print("No answers found to submit")

if __name__ == "__main__":
    main()