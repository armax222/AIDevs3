import json
from utilities.common import AIDevsClient, OpenAIClient
from utilities.config import AI_DEVS_API_KEY, S01E05_TASK_URL, S01E05_REPORT_URL

def main():
    # Initialize clients
    client_aidevs = AIDevsClient()
    client_openai = OpenAIClient()

    # Configuration
    TASK_NAME = "CENZURA"
    API_KEY = AI_DEVS_API_KEY
    DATA_URL = S01E05_TASK_URL
    SUBMIT_URL = S01E05_REPORT_URL

    # Step 1: Retrieve data using the client method
    data = ''.join(client_aidevs.fetch_data(DATA_URL))
    print("Original Text: " + data)

    if data:
        # Step 2: Censor personal information
        messages = [
            {"role": "system", "content": (
                "You are a helpful assistant that censors personal information in a text. "
                "Replace all names, ages, cities, and street addresses with the word 'CENZURA'. "
                "YOU MUST KEEP the rest of the text unchanged, including all spaces, punctuation, and words."
            )},
            {"role": "user", "content": data}
        ]
        censored_text = client_openai.get_completion(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.1
        ).strip()
        print("Censored Text: " + censored_text)

        # Step 3: Prepare the payload
        payload = {
            "task": TASK_NAME,
            "apikey": API_KEY,
            "answer": censored_text
        }

        # Step 4: Submit the censored data using the client method
        response = client_aidevs.submit_answer(answer=payload, submit_url=SUBMIT_URL)

        # Handle response
        if response:
            print(f"Request successful! Response: {response}")
        else:
            print("Failed to submit the censored data.")
    else:
        print("Failed to retrieve data.")

if __name__ == "__main__":
    main()
