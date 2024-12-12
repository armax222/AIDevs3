import os
import base64
import requests
from bs4 import BeautifulSoup, NavigableString
from utilities.common import AIDevsClient, OpenAIClient
from utilities.config import AI_DEVS_API_KEY, S02E05_DATA_URL, S02E05_TASK_URL, S02E05_REPORT_URL

# =========================================================
# Configuration
# =========================================================
def get_config():
    return {
        'task_name': "arxiv",
        'article_url': S02E05_DATA_URL,
        'questions_url': S02E05_TASK_URL,
        'submit_url': S02E05_REPORT_URL,
        'data_folder': "s02e05"
    }

# =========================================================
# Helper Functions
# =========================================================
def download_and_save_media(url, folder, filename):
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)
        with open(path, 'wb') as f:
            f.write(response.content)
        return path
    return None

def node_to_markdown(node, base_url, data_folder, openai_client, images_content, audio_content):
    """Recursively convert HTML node to Markdown, inserting image/audio descriptions inline."""
    parts = []
    if isinstance(node, NavigableString):
        text = node.strip()
        if text:
            parts.append(text)
    else:
        # It's a tag
        if node.name == 'img':
            # Process image
            img_url = node.get('src')
            if img_url and not img_url.startswith(('http://', 'https://')):
                img_url = base_url + img_url
            
            img_path = download_and_save_media(img_url, data_folder, os.path.basename(img_url))
            if img_path:
                encoded_image = base64.b64encode(open(img_path, "rb").read()).decode('utf-8')
                messages = [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in detail."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                    ]
                }]
                image_description = openai_client.get_completion(messages=messages, model="gpt-4o", temperature=0.1)
                images_content.append(image_description)  # Keep track
                # Insert inline image description
                parts.append(f"\n\n> {image_description}\n\n")

        elif node.name == 'audio':
            # Process audio
            audio_source = node.find('source')
            audio_url = audio_source.get('src') if audio_source else node.get('src')
            if audio_url and not audio_url.startswith(('http://', 'https://')):
                audio_url = base_url + audio_url

            audio_path = download_and_save_media(audio_url, data_folder, os.path.basename(audio_url))
            if audio_path:
                transcript = openai_client.transcribe(audio_path).get('text', '')
                audio_content.append(transcript)  # Keep track
                # Insert inline audio transcript as code block
                parts.append(f"\n\n```\n{transcript}\n```\n\n")

        else:
            # For other tags, process children
            for child in node.children:
                parts.append(node_to_markdown(child, base_url, data_folder, openai_client, images_content, audio_content))

            # Add a paragraph break after certain block-level elements
            if node.name in ['p', 'div', 'section', 'article', 'br']:
                parts.append("\n\n")

    return "".join(parts)

def process_article(config, client_openai):
    """Process the article and produce a Markdown file with images and audio inline."""
    response = requests.get(config['article_url'] + "arxiv-draft.html")
    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = config['article_url']  # Base URL for relative paths

    images_content = []
    audio_content = []

    # Convert the entire body into Markdown
    body = soup.find('body')
    if not body:
        body = soup  # fallback if no body tag

    markdown_content = node_to_markdown(body, base_url, config['data_folder'], client_openai, images_content, audio_content)

    # Create Markdown file
    md_filename = os.path.join(config['data_folder'], "article_content.md")
    with open(md_filename, 'w', encoding='utf-8') as md_file:
        md_file.write("# Article Content\n\n")
        md_file.write(markdown_content.strip() + "\n")

    return {
        'text': markdown_content,
        'images': images_content,
        'audio': audio_content
    }

def get_questions(config):
    """Fetch questions from the API."""
    response = requests.get(config['questions_url'])
    if response.status_code == 200:
        try:
            return response.json()
        except:
            clean_text = response.text.strip().encode('utf-8').decode('utf-8-sig')
            import json
            try:
                return json.loads(clean_text)
            except:
                lines = clean_text.split('\n')
                return {f"question_{i+1}": line.strip() for i, line in enumerate(lines) if line.strip()}
    return None

def main():
    # Initialize clients
    client_aidevs = AIDevsClient()
    client_openai = OpenAIClient()
    
    # Get configuration
    config = get_config()

    # Process article
    article_content = process_article(config, client_openai)

    # Get questions
    questions = get_questions(config)
    print(questions)

    # Read context from article_content.md
    article_content = open(os.path.join(config['data_folder'], "article_content.md"), "r").read()

    if questions:
        # Generate answers using GPT-4
        messages = [{
            "role": "system",
            "content": "You are an AI assistant helping to answer questions about Professor Maj's article. "
                      "Provide concise, one-sentence answers strictly based on the provided context."
                      "Format your answers as a simple list, one per line."
        }, {
            "role": "user",
            "content": f"""Here is the content from the article:

Context:
{article_content}

Please answer these questions with one sentence each:
{questions}"""
        }]

        answers = client_openai.get_completion(
            messages=messages,
            model="gpt-4o",
            temperature=0.1
        )

        # Parse answers into required format
        answers_list = [answer.strip() for answer in answers.split('\n') if answer.strip()]
        
        # Create formatted answer dictionary
        formatted_answer = {}
        for question_id, answer in zip(questions.keys(), answers_list):
            numeric_id = question_id.split('_')[-1]
            formatted_id = f"{int(numeric_id):02d}"
            formatted_answer[formatted_id] = answer

        print(formatted_answer)

        # Submit answers
        payload = {
            "task": config['task_name'],
            "apikey": AI_DEVS_API_KEY,
            "answer": formatted_answer
        }

        response = client_aidevs.submit_answer(
            answer=payload,
            submit_url=config['submit_url']
        )
        print(f"Submission response: {response}")
    else:
        print("Failed to retrieve questions.")

if __name__ == "__main__":
    main()