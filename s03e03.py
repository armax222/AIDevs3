#!/usr/bin/env python3
"""
Module for handling database queries and submissions for AI Devs task.
"""

# Standard library imports
import requests
from typing import Dict, List, Optional, Union

# Local imports
from utilities.common import AIDevsClient, OpenAIClient
from utilities.config import AI_DEVS_API_KEY, S03E03_TASK_URL, S03E03_REPORT_URL


class DatabaseQueryManager:
    """Manages database queries and interactions with AI Devs API."""

    def __init__(self) -> None:
        """Initialize the DatabaseQueryManager with necessary clients and configuration."""
        self.client_aidevs: AIDevsClient = AIDevsClient()
        self.client_openai: OpenAIClient = OpenAIClient()
        self.task_name: str = "database"
        self.api_url: str = S03E03_TASK_URL
        self.submit_url: str = S03E03_REPORT_URL

    def get_table_info(self) -> Optional[Dict]:
        """
        Retrieve table information from the database.

        Returns:
            Optional[Dict]: Dictionary containing table structures or None if failed
        """
        payload = {
            "task": self.task_name,
            "apikey": AI_DEVS_API_KEY,
            "query": "show tables"
        }
        response = requests.post(self.api_url, json=payload).json()
        
        if not response.get('reply'):
            return None

        table_key = list(response['reply'][0].keys())[0]
        tables = [table[table_key] for table in response['reply']]
        print("Tables:", tables)
        
        table_structures = {}
        for table in tables:
            payload["query"] = f"show create table {table}"
            structure = requests.post(self.api_url, json=payload).json()
            print(f"\nStructure for {table}:", structure)
            if 'reply' in structure:
                table_structures[table] = structure
        
        return table_structures

    def generate_sql_query(self, table_info: Dict) -> str:
        """
        Generate SQL query using OpenAI based on table structures.

        Args:
            table_info (Dict): Dictionary containing table structures

        Returns:
            str: Generated SQL query
        """
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
        
        return self.client_openai.get_completion(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.1
        )

    def execute_query(self, sql_query: str) -> Dict:
        """
        Execute the generated SQL query.

        Args:
            sql_query (str): SQL query to execute

        Returns:
            Dict: Response from the API
        """
        test_payload = {
            "task": self.task_name,
            "apikey": AI_DEVS_API_KEY,
            "query": sql_query
        }
        return requests.post(self.api_url, json=test_payload).json()

    def submit_answer(self, dc_ids: List[int]) -> Dict:
        """
        Submit the answer to AI Devs.

        Args:
            dc_ids (List[int]): List of datacenter IDs to submit

        Returns:
            Dict: Response from the submission
        """
        return self.client_aidevs.submit_answer(
            answer={
                "task": self.task_name,
                "apikey": AI_DEVS_API_KEY,
                "answer": dc_ids
            },
            submit_url=self.submit_url
        )


def main() -> None:
    """Main execution function."""
    manager = DatabaseQueryManager()
    
    # Step 1: Get table structures
    table_info = manager.get_table_info()
    if not table_info:
        print("Failed to get table information")
        return
    
    # Step 2: Generate and test SQL query
    sql_query = manager.generate_sql_query(table_info)
    print("Generated SQL query:", sql_query)
    
    test_response = manager.execute_query(sql_query)
    print("\nQuery test response:", test_response)
    
    # Step 3: Submit answer
    if 'reply' in test_response:
        dc_ids = [int(row['dc_id']) for row in test_response['reply']]
        print("DC IDs:", dc_ids)
        
        response = manager.submit_answer(dc_ids)
        print("Submission response:", response)
    else:
        print("Query execution failed")


if __name__ == "__main__":
    main()