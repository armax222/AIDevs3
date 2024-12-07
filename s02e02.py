import os
import base64
from utilities.common import OpenAIClient

# =========================================================
# Configuration
# =========================================================
def get_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return {
        'data_folder': os.path.join(script_dir, "s02e02"),
        'image_files': [
            "fragment1.png",
            "fragment2.png", 
            "fragment3.png",
            "fragment4.png"
        ]
    }

# =========================================================
# Helper Functions
# =========================================================
def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def validate_files(data_folder: str, image_files: list) -> bool:
    if not os.path.isdir(data_folder):
        print(f"Error: The folder '{data_folder}' does not exist.")
        return False

    for img_file in image_files:
        img_path = os.path.join(data_folder, img_file)
        if not os.path.isfile(img_path):
            print(f"Error: Missing image file '{img_path}'.")
            return False
    return True

def encode_all_images(data_folder: str, image_files: list) -> dict:
    encoded_images = {}
    for img_file in image_files:
        img_path = os.path.join(data_folder, img_file)
        encoded_images[img_file] = encode_image(img_path)
    return encoded_images

def construct_messages(encoded_images: dict) -> list:
    return [{
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

def main():
    # Get configuration
    config = get_config()
    
    # Validate files
    if not validate_files(config['data_folder'], config['image_files']):
        return
    
    # Encode images
    encoded_images = encode_all_images(config['data_folder'], config['image_files'])
    
    # Construct messages
    messages = construct_messages(encoded_images)
    
    # Get analysis from OpenAI
    client = OpenAIClient(model="gpt-4o")
    result = client.get_completion(messages=messages, temperature=0, max_tokens=1200)
    print(result)

if __name__ == "__main__":
    main()
