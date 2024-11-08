# Import necessary modules
from utilities.common import AIDevsClient
from utilities.config import S00E01_DATA_URL

# Configuration
task_name = "POLIGON"  # Consider moving to a config file if it changes often
data_url = S00E01_DATA_URL

# Initialize the AIDevs client
client_aidevs = AIDevsClient()

def main():
    """Main function to retrieve data and submit answers."""
    # Step 1: Retrieve data using the client method
    data_list = client_aidevs.fetch_data(data_url)

    # Step 2: Submit the answer if data is successfully retrieved
    if data_list:
        submit_response = client_aidevs.submit_answer(task_name, data_list)
        print("Submit response:", submit_response)
    else:
        print("No data retrieved from the URL.")

# Entry point of the script
if __name__ == "__main__":
    main()