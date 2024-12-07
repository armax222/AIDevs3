import os
import base64
from utilities.common import OpenAIClient

# =========================================================
# Configuration
# =========================================================
script_dir = os.path.dirname(os.path.abspath(__file__)) # Get the directory of the current script
DATA_FOLDER = os.path.join(script_dir, "s02e02")
IMAGE_FILES = [
    "fragment1.png",
    "fragment2.png", 
    "fragment3.png",
    "fragment4.png"
]

# =========================================================
# Helper Functions
# =========================================================
def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# =========================================================
# Step 1: Validate Data Directory and Files
# =========================================================
if not os.path.isdir(DATA_FOLDER):
    print(f"Error: The folder '{DATA_FOLDER}' does not exist.")
    exit(1)

for img_file in IMAGE_FILES:
    img_path = os.path.join(DATA_FOLDER, img_file)
    if not os.path.isfile(img_path):
        print(f"Error: Missing image file '{img_path}'.")
        exit(1)

# =========================================================
# Step 2: Encode Images
# =========================================================
encoded_images = {}
for img_file in IMAGE_FILES:
    img_path = os.path.join(DATA_FOLDER, img_file)
    encoded_images[img_file] = encode_image(img_path)

# =========================================================
# Step 3: Construct Message for Analysis
# =========================================================
messages = [{
    "role": "user",
    "content": [
        {
            "type": "text",
            "text": 
            """
                Jesteś ekspertem od map, jakie to może być miasto:
                - przechodzi przez nie droga o numerze 534
                - ma spichlerze i twierdze
                - ma cmentarz ewangelicko-augsburski blisko ulic parkowa i cmentarna
            """
        }
    ] + [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}
        }
        for img_data in encoded_images.values()
    ]
}]

# =========================================================
# Step 4: Get Analysis from OpenAI
# =========================================================
client = OpenAIClient(model="gpt-4o")
result = client.get_completion(messages=messages, temperature=0, max_tokens=1200)
print(result)
