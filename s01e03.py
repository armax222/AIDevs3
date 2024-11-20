import json
from utilities.common import AIDevsClient, OpenAIClient
from utilities.config import S01E03_TASK_URL, AI_DEVS_API_KEY, S01E03_REPORT_URL

# Initialize clients
client_aidevs = AIDevsClient()
client_openai = OpenAIClient()

# Configuration
TASK_NAME = "JSON"
API_KEY = AI_DEVS_API_KEY
DATA_URL = S01E03_TASK_URL
SUBMIT_URL = S01E03_REPORT_URL

def main():
    # Step 1: Retrieve data using the client method
    data = client_aidevs.fetch_data(DATA_URL)

    if data:
        # Parse the data
        data_str = ''.join(data)
        data_json = json.loads(data_str)

        # Process test data
        for item in data_json.get('test-data', []):
            if 'test' in item:
                # Query LLM for conceptual questions
                test_question = item['test'].get('q')
                messages = [
                    {"role": "system", "content": "You are a helpful assistant that provides very short answers to user questions."},
                    {"role": "user", "content": test_question}
                ]
                llm_answer = client_openai.get_completion(messages=messages, model="gpt-4o-mini", temperature=0.1).strip()
                print(f"Test question: {test_question}, LLM Answer: {llm_answer}")
                item['test']['a'] = llm_answer
            else:
                # Evaluate mathematical expressions
                question = item.get('question')
                correct_answer = eval(question)
                if item.get('answer') != correct_answer:
                    print(f"Correcting: {question} from {item['answer']} to {correct_answer}")
                    item['answer'] = correct_answer

        # Prepare the complete payload
        payload = {
            "task": TASK_NAME,
            "apikey": API_KEY,
            "answer": {
                "apikey": API_KEY,  # Include the API key in the answer
                "description": data_json.get("description"),
                "test-data": data_json.get("test-data")
            }
        }

        # Submit payload using the modified AIDevsClient
        response = client_aidevs.submit_answer(task_name=TASK_NAME, answer=payload, submit_url=SUBMIT_URL)

        if response:
            print(f"Request successful! Response: {response}")
        else:
            print("Failed to submit the answer.")
    else:
        print("Failed to retrieve data.")

if __name__ == "__main__":
    main()
