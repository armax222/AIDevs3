# Import necessary modules
from utilities.common import AIDevsClient
from utilities.config import S00E01_DATA_URL, AI_DEVS_API_ENDPOINT, AI_DEVS_API_KEY

# Initialize the client
client_aidevs = AIDevsClient()

# Configuration
task_name = "POLIGON"
data_url = S00E01_DATA_URL
submit_url = AI_DEVS_API_ENDPOINT

def main():
    # Step 1: Retrieve data using the client method
    answer_data = client_aidevs.fetch_data(data_url)

    # Step 2: Submit the answer
    if answer_data:
        # Prepare the payload in the correct structure
        payload = {
            "task": task_name,
            "apikey": AI_DEVS_API_KEY,
            "answer": answer_data  
        }

        # Submit the payload
        submit_response = client_aidevs.submit_answer(task_name=task_name, answer=payload, submit_url=submit_url)
        
        # Handle response
        if submit_response:
            print("Submit response:", submit_response)
        else:
            print("Submission failed.")
    else:
        print("Failed to retrieve data.")

if __name__ == "__main__":
    main()
