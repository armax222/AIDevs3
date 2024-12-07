from utilities.common import AIDevsClient, OpenAIClient
from utilities.config import AI_DEVS_API_KEY, S02E03_TASK_URL, S02E03_REPORT_URL

def get_config():
    return {
        'task_name': "robotid",
        'api_key': AI_DEVS_API_KEY,
        'submit_url': S02E03_REPORT_URL,
        'task_url': S02E03_TASK_URL
    }

def create_dalle_prompt(client: OpenAIClient, description: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that creates detailed DALL-E prompts from descriptions."
        },
        {
            "role": "user",
            "content": f"Create a detailed DALL-E prompt for a robot based on this description: {description}"
        }
    ]
    
    return client.get_completion(
        messages=messages,
        model="gpt-4o",
        temperature=0.7
    )

def generate_robot_image(client: OpenAIClient, dalle_prompt: str) -> str:
    image_url = client.generate_image(
        prompt=dalle_prompt,
        model="dall-e-3",
        size="1024x1024",
        quality="standard",
        format="png"
    )
    
    if image_url:
        print(f"Generated image URL: {image_url}")
    else:
        print("Failed to generate image")
    
    return image_url

def submit_answer(client: AIDevsClient, task_name: str, api_key: str, submit_url: str, image_url: str) -> dict:
    payload = {
        "task": task_name,
        "apikey": api_key,
        "answer": image_url
    }
    
    response = client.submit_answer(answer=payload, submit_url=submit_url)
    print(f"Submission response: {response}")
    return response

def main():
    # Get configuration
    config = get_config()
    
    # Initialize clients
    client_aidevs = AIDevsClient()
    client_openai = OpenAIClient()
    
    # Get task data
    data = client_aidevs.fetch_data(config['task_url'])
    
    # Generate DALL-E prompt and image
    dalle_prompt = create_dalle_prompt(client_openai, data)
    image_url = generate_robot_image(client_openai, dalle_prompt)
    
    if image_url:
        # Submit answer
        submit_answer(
            client_aidevs,
            config['task_name'],
            config['api_key'],
            config['submit_url'],
            image_url
        )

if __name__ == "__main__":
    main()