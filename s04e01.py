# Standard library imports
import requests
import base64

# Local imports
from utilities.common import AIDevsClient, OpenAIClient
from utilities.config import AI_DEVS_API_KEY, S04E01_TASK_URL, S04E01_REPORT_URL

# =========================================================
# Constants
# =========================================================
TASK_NAME = "photos"
API_URL = S04E01_REPORT_URL
PHOTOS_URL = S04E01_TASK_URL
SUBMIT_URL = S04E01_REPORT_URL

# =========================================================
# Helper Functions
# =========================================================
def get_info(url):
    """Get image description or status (dark/bright/damaged) from URL."""
    try:
        print(f"\n🔍 Analyzing image: {url}")
        url = PHOTOS_URL + url.strip("'")
        
        response = requests.get(url)
        if response.status_code != 200:
            print("❌ Error downloading image")
            return "Error downloading image"
            
        encoded = base64.b64encode(response.content).decode('utf-8')
        
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": """
                        If image is dark - return 'BRIGHTEN'
                        If bright - return 'DARKEN'
                        If damaged - return 'REPAIR'
                        Otherwise describe this person focusing on:
                        - Physical characteristics (face, hair, eyes)
                        - Clothing and style
                        - Distinctive features
                    """
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{encoded}"}
                }
            ]
        }]
        
        result = client_openai.get_completion(
            messages=messages,
            model="gpt-4o",
            temperature=0.1
        )
        print(f"📝 Analysis result: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return None

def process_image_command(image_name, command=None):
    """Process image with optional command and get next image name."""
    try:
        print(f"\n🔧 Processing image: {image_name}")
        print(f"Command: {command if command else 'No command - getting info only'}")
        
        if command:
            payload = {
                "task": TASK_NAME,
                "apikey": AI_DEVS_API_KEY,
                "answer": f"{command} {image_name}"
            }

            response = client_aidevs.submit_answer(
                answer=payload,
                submit_url=SUBMIT_URL
            )
            print(f"📥 Response received: {response}")

            messages = [
                {
                    "role": "system",
                    "content": "Extract only the filename from the text."
                },
                {
                    "role": "user",
                    "content": response['message']
                }
            ]

            next_image = client_openai.get_completion(
                messages=messages,
                model="gpt-4o",
                temperature=0.1
            )
            print(f"📸 Next image: {next_image}")
            return next_image
        else:
            return get_info(image_name)

    except Exception as e:
        print(f"❌ Error processing command for image {image_name}: {e}")
        return None

def process_image_until_complete(initial_image):
    """Process a single image until it's fully corrected and returns a description."""
    current_image = initial_image
    
    while current_image:
        image_status = get_info(current_image)
        
        if image_status in ["REPAIR", "DARKEN", "BRIGHTEN"]:
            current_image = process_image_command(current_image, image_status)
        else:
            return image_status
            
    return None

def main():
    """Main execution function."""
    global client_aidevs, client_openai
    
    # =========================================================
    # Initialize clients
    # =========================================================
    client_aidevs = AIDevsClient()
    client_openai = OpenAIClient()

    # =========================================================
    # Step 1: Start conversation and get photos
    # =========================================================
    payload = {
        "task": TASK_NAME,
        "apikey": AI_DEVS_API_KEY,
        "answer": "START"
    }

    response = client_aidevs.submit_answer(
        answer=payload,
        submit_url=SUBMIT_URL
    )

    message_of_photos = response['message']

    messages = [
        {
            "role": "system",
            "content": "Extract image names from the text, return only the filenames separated by spaces"
        },
        {
            "role": "user",
            "content": message_of_photos
        }
    ]

    list_of_urls = client_openai.get_completion(
        messages=messages,
        model="gpt-4o",
        temperature=0.1
    ).split()

    print(f"📸 Found images: {list_of_urls}")

    # =========================================================
    # Step 2: Process images and generate descriptions
    # =========================================================
    descriptions = []
    for image in list_of_urls:
        description = process_image_until_complete(image)
        if description:
            descriptions.append(description)

    # =========================================================
    # Step 3: Generate final description
    # =========================================================
    messages = [
        {
            "role": "system",
            "content": """
            Jesteś ekspertem w tworzeniu rysopisów osób. Na podstawie opisów:
            1. Przeanalizuj wszystkie opisy i znajdź powtarzające się cechy
            2. Stwórz zwięzły rysopis w języku polskim, skupiając się na:
               - Stałych cechach fizycznych (twarz, włosy, oczy)
               - Charakterystycznych znakach szczególnych
               - Typowym stylu ubioru
            3. Użyj wypunktowania dla przejrzystości
            4. Pomiń zmienne elementy jak tło czy pozy
            """
        },
        {
            "role": "user",
            "content": f"Stwórz rysopis Barbary na podstawie tych opisów:\n\n{descriptions}"
        }
    ]

    rysopis = client_openai.get_completion(
        messages=messages,
        model="gpt-4o",
        temperature=0.1
    )

    print("\n📝 Rysopis Barbary:")
    print(rysopis)

    # =========================================================
    # Step 4: Submit final answer
    # =========================================================
    final_payload = {
        "task": TASK_NAME,
        "apikey": AI_DEVS_API_KEY,
        "answer": rysopis
    }

    response = client_aidevs.submit_answer(
        answer=final_payload,
        submit_url=SUBMIT_URL
    )

    print(f"Final response: {response}")

if __name__ == "__main__":
    main()