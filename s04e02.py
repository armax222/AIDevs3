# Standard library imports
import os
import shutil
import zipfile
from typing import List

# Third-party imports
import numpy as np
import requests
from sklearn.tree import DecisionTreeClassifier

# Local imports
from utilities.common import AIDevsClient, OpenAIClient
from utilities.config import AI_DEVS_API_KEY, S04E02_TASK_URL, S04E02_REPORT_URL

# =========================================================
# Configuration
# =========================================================
TASK_NAME = "research"
ZIP_URL = S04E02_TASK_URL
ZIP_PATH = "s04e02/lab_data.zip"
EXTRACT_FOLDER = "s04e02/files"
SUBMIT_URL = S04E02_REPORT_URL

# Initialize clients
client_aidevs = AIDevsClient()
client_openai = OpenAIClient()

# =========================================================
# Helper Functions
# =========================================================
def download_zip(url: str, path: str) -> bool:
    """Download ZIP file from URL.
    
    Args:
        url (str): URL to download from
        path (str): Path to save the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading ZIP: {e}")
        return False

def process_verification_data() -> List[str]:
    """Process verification data using a Decision Tree classifier.
    
    Returns:
        List[str]: List of valid identifiers sorted alphabetically
    """
    # Prepare training data
    X_train = []  # Features
    y_train = []  # Labels (1 for correct, 0 for incorrect)
    
    # Process correct samples (label 1)
    for line in correct_content:
        if line.strip():
            numbers = [int(n) for n in line.strip().split(',')]
            X_train.append(numbers)
            y_train.append(1)
    
    # Process incorrect samples (label 0)
    for line in incorrect_content:
        if line.strip():
            numbers = [int(n) for n in line.strip().split(',')]
            X_train.append(numbers)
            y_train.append(0)
    
    # Convert to numpy arrays
    X_train = np.array(X_train)
    y_train = np.array(y_train)
    
    # Train decision tree
    clf = DecisionTreeClassifier(random_state=42)
    clf.fit(X_train, y_train)
    
    # Process verification data
    valid_identifiers = []
    for line in verify_content.split('\n'):
        if '=' in line:
            identifier, values = line.split('=')
            identifier = identifier.strip()
            numbers = [int(n) for n in values.strip().split(',')]
            
            # Make prediction
            if clf.predict([numbers])[0] == 1:  # If classified as correct
                valid_identifiers.append(identifier)
    
    return sorted(valid_identifiers)

def main():
    """Main execution function."""
    try:
        # Clean up and create directories
        if os.path.exists(os.path.dirname(ZIP_PATH)):
            shutil.rmtree(os.path.dirname(ZIP_PATH))
        os.makedirs(os.path.dirname(ZIP_PATH), exist_ok=True)
        os.makedirs(EXTRACT_FOLDER, exist_ok=True)

        # Download and extract ZIP file
        if not download_zip(ZIP_URL, ZIP_PATH):
            print("Failed to download ZIP file")
            return

        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_FOLDER)

        # Read input files
        with open(os.path.join(EXTRACT_FOLDER, 'verify.txt'), 'r') as file:
            global verify_content
            verify_content = file.read()
        with open(os.path.join(EXTRACT_FOLDER, 'correct.txt'), 'r') as file:
            global correct_content
            correct_content = file.read().split('\n')
        with open(os.path.join(EXTRACT_FOLDER, 'incorrect.txt'), 'r') as file:
            global incorrect_content
            incorrect_content = file.read().split('\n')

        # Process data and get valid identifiers
        valid_ids = process_verification_data()
        print("Valid identifiers:", valid_ids)

        # Submit answer
        response = client_aidevs.submit_answer(
            answer={
                "task": TASK_NAME,
                "apikey": AI_DEVS_API_KEY,
                "answer": valid_ids
            },
            submit_url=SUBMIT_URL
        )

        print(f"\nSubmission response: {response}")

    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()