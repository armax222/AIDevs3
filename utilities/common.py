# Standard library imports
import requests

# Third-party imports
import openai  # Import the openai module

# Local imports
from utilities.config import AI_DEVS_API_ENDPOINT, AI_DEVS_API_KEY, OPEN_AI_API_KEY



class OpenAIClient:
    """
    A client to interact with OpenAI's APIs, including Chat Completion and Whisper transcription.
    """

    def __init__(self, model="gpt-4"):
        """
        Initialize the OpenAI client using the API key.
        """
        self.api_key = OPEN_AI_API_KEY
        self.model = model  # Default model for Chat Completion
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def get_completion(self, messages, model=None, max_tokens=1500, temperature=0.2):
        """
        Get a completion from OpenAI using the chat completion API.

        :param messages: A list of messages in ChatML format (role-content pairs).
        :param model: The model to use (defaults to self.model if not specified).
        :param max_tokens: Maximum tokens for the response.
        :param temperature: The sampling temperature for the model.
        :return: The model's response or None if an error occurs.
        """
        model_to_use = model or self.model

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": model_to_use,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def transcribe(self, audio_file):
        """
        Transcribes an audio file using OpenAI's Whisper API.

        :param audio_file: Path to the audio file to transcribe.
        :return: Transcription result as a dictionary.
        """
        try:
            with open(audio_file, "rb") as audio:
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers=self.headers,
                    files={"file": audio},
                    data={"model": "whisper-1"}
                )
                response.raise_for_status()
                return response.json()  # Returns the full transcription response
        except Exception as e:
            print(f"An error occurred during transcription: {e}")
            return None
        
    def generate_image(self, prompt: str, model: str = "dall-e-3", size: str = "1024x1024", 
                    quality: str = "standard", format: str = "png") -> str:
        """Generate an image using DALL-E and return the URL."""
        try:
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=self.headers,
                json={
                    "model": model,
                    "prompt": prompt,
                    "n": 1,
                    "size": size,
                    "quality": quality,
                    "response_format": "url"
                }
            )
            response.raise_for_status()
            return response.json()["data"][0]["url"]
        except Exception as e:
            print(f"Error generating image: {e}")
            return None


class AIDevsClient:
    """
    A client to interact with the AIDevs API.
    Provides methods to fetch data and submit answers.
    """

    def __init__(self, base_url=AI_DEVS_API_ENDPOINT, api_key=AI_DEVS_API_KEY):
        """
        Initialize the AIDevsClient.
        
        :param base_url: Base URL for the API.
        :param api_key: Authentication key for the API.
        """
        self.base_url = base_url
        self.api_key = api_key

    def fetch_data(self, url):
        """
        Fetch data from a specified URL outside of the main API.
        
        :param url: URL to retrieve data from.
        :return: List of strings (lines from the response) or None if request fails.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text.strip().split("\n")  # Returns list of lines
        except requests.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return None

    def submit_answer(self, answer, submit_url=None):
        """
        Submit an answer for a task, including API key in the payload as required.
        
        :param answer: The full payload to be sent.
        :param submit_url: URL for submission (overrides the default endpoint).
        :return: API response or None if request fails.
        """
        url = submit_url if submit_url else f"{self.base_url}/verify"
        
        try:
            response = requests.post(
                url, 
                json=answer,
                headers={"Content-Type": "application/json"}
            )
            if response.ok:
                return response.json()
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
        except requests.RequestException as e:
            print(f"Error in POST request to {url}: {e}")
            return None

