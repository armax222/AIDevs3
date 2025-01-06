import requests
from utilities.common import OpenAIClient, AIDevsClient
from utilities.config import AI_DEVS_API_KEY, S03E04_REPORT_URL, S03E04_TASK_URL, S03E04_PEOPLE_URL, S03E04_CITIES_URL

# =========================================================
# Configuration
# =========================================================
TASK_NAME = "loop"
NOTE_URL = S03E04_TASK_URL
PEOPLE_API = S03E04_PEOPLE_URL
PLACES_API = S03E04_CITIES_URL
SUBMIT_URL = S03E04_REPORT_URL

# Initialize clients
client_openai = OpenAIClient()
client_aidevs = AIDevsClient()

# =========================================================
# Helper Functions
# =========================================================
def query_api(api_url, query):
    """Query the specified API with the given query."""
    payload = {
        "apikey": AI_DEVS_API_KEY,
        "query": query
    }
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        if response.status_code != 400:  # Only print non-400 errors
            print(f"Error querying API {api_url} with query {query}: {e}")
        return None

def cities_for_names(names):
    all_cities = set()
    for name in names:
        result = query_api(PEOPLE_API, name)
        if result:
            # Split and clean in one step
            all_cities.update(city for city in result['message'].split() 
                            if not (city.startswith('[') or city.startswith('http')))
    return all_cities

def names_for_cities(cities):
    all_names = set()
    for city in cities:
        result = query_api(PLACES_API, city)
        if result:
            # Split and clean in one step
            all_names.update(name for name in result['message'].split() 
                           if not (name.startswith('[') or name.startswith('http')))
    return all_names

def main():
    # =========================================================
    # Step 1: Get and analyze note content
    # =========================================================
    response = requests.get(NOTE_URL)
    note = response.text if response.status_code == 200 else None

    if not note:
        print("Failed to retrieve note")
        return

    # Extract names and cities using OpenAI
    messages = [
        {
            "role": "system",
            "content": (
                "You are a named entity recognition expert. Extract two lists from the given text:\n"
                "1. List of person names in nominative case (mianownik) without Polish characters\n"
                "2. List of city names without Polish characters\n"
                "Format your response exactly like this example:\n"
                "names = ['JOHN', 'ALICE']\n"
                "cities = ['LONDON', 'PARIS']"
            )
        },
        {
            "role": "user",
            "content": f"Extract names and cities from this text:\n\n{note}"
        }
    ]
    
    response = client_openai.get_completion(
        messages=messages,
        model="gpt-4",
        temperature=0.1
    )
    
    # Create a local dictionary to store the executed variables
    local_vars = {}
    exec(response, globals(), local_vars)
    
    # Extract names and cities from the local dictionary
    names = local_vars.get('names', [])
    cities = local_vars.get('cities', [])
    
    print("Note content:")
    print(note)
    print("\nExtracted entities:")
    print("Names:", names)
    print("Cities:", cities)

    # =========================================================
    # Step 2: Search for Barbara's location
    # =========================================================
    found_city = ""
    while found_city == "":
        old_cities = set(cities)
        
        names = names_for_cities(cities)
        print("Found names:", names)
        
        cities = cities_for_names(names)
        
        new_cities = set(cities) - old_cities
        print("Difference (new cities):", new_cities)
        
        for city in new_cities:
            result = query_api(PLACES_API, city)
            if result and "BARBARA" in result['message']:
                print("Found Barbara in:", city)
                found_city = city

    # =========================================================
    # Step 3: Submit answer
    # =========================================================
    response = client_aidevs.submit_answer(
        answer={"task": TASK_NAME, "apikey": AI_DEVS_API_KEY, "answer": found_city},
        submit_url=SUBMIT_URL
    )
    print(response)


if __name__ == "__main__":
    main()