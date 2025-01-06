# Standard library imports
import requests

# Local imports
from utilities.common import AIDevsClient, OpenAIClient
from utilities.config import AI_DEVS_API_KEY, S03E03_TASK_URL, S03E03_REPORT_URL

# =========================================================
# Configuration
# =========================================================
SUBMIT_URL = S03E03_REPORT_URL
TASK_NAME = "database"
API_URL = S03E03_TASK_URL

def get_table_info():
    """Get database table structures."""
    # First get list of tables
    payload = {
        "task": TASK_NAME,
        "apikey": AI_DEVS_API_KEY,
        "query": "show tables"
    }
    response = requests.post(API_URL, json=payload).json()
    
    # Extract table names dynamically by getting the first key from the first dictionary
    if 'reply' in response and response['reply']:
        table_key = list(response['reply'][0].keys())[0]  # Gets the first (and only) key dynamically
        tables = [table[table_key] for table in response['reply']]
        print("Tables:", tables)
        
        # Then get structure for each table
        table_structures = {}
        for table in tables:
            payload["query"] = f"show create table {table}"
            structure = requests.post(API_URL, json=payload).json()
            print(f"\nStructure for {table}:", structure)
            if 'reply' in structure:
                table_structures[table] = structure
        
        return table_structures
    
    return None

def generate_sql_query(table_info, client_openai):
    """Generate SQL query using OpenAI."""
    messages = [
        {
            "role": "system",
            "content": "You are an SQL expert. Generate a SQL query based on the table structures provided. Return only the query without any formatting."
        },
        {
            "role": "user",
            "content": f"""
            Table structures:
            {table_info}
            
            Question: Which active datacenter IDs are managed by users who are currently on vacation (inactive)?
            """
        }
    ]
    
    return client_openai.get_completion(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.1
    )

def test_query(sql_query):
    """Test the generated SQL query."""
    test_payload = {
        "task": TASK_NAME,
        "apikey": AI_DEVS_API_KEY,
        "query": sql_query
    }
    
    return requests.post(API_URL, json=test_payload).json()

def submit_results(dc_ids, client_aidevs):
    """Submit the final results."""
    return client_aidevs.submit_answer(
        answer={
            "task": TASK_NAME,
            "apikey": AI_DEVS_API_KEY,
            "answer": dc_ids
        },
        submit_url=SUBMIT_URL
    )

def main():
    # Initialize clients
    client_aidevs = AIDevsClient()
    client_openai = OpenAIClient()

    # Step 1: Get table structures
    table_info = get_table_info()
    if not table_info:
        print("Failed to get table information")
        return
    
    # Step 2: Generate and test SQL query
    sql_query = generate_sql_query(table_info, client_openai)
    print("Generated SQL query:", sql_query)
    
    # Step 3: Test the query
    test_response = test_query(sql_query)
    print("\nQuery test response:", test_response)
    
    # Step 4: Process and submit results
    if 'reply' in test_response:
        dc_ids = [int(row['dc_id']) for row in test_response['reply']]
        print("DC IDs:", dc_ids)
        
        response = submit_results(dc_ids, client_aidevs)
        print("Submission response:", response)
    else:
        print("Failed to get valid response from query test")

if __name__ == "__main__":
    main()