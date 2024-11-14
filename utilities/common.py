# Standard library imports
import requests

# Third-party imports
from openai import OpenAI

# Local imports
from utilities.config import AI_DEVS_API_ENDPOINT, AI_DEVS_API_KEY, OPEN_AI_API_KEY

class OpenAIClient:
    """
    A client to interact with OpenAI's Chat Completion API for generating responses.
    """

    def __init__(self, model="gpt-4o"):
        """
        Initialize the OpenAI client using the API key.
        """
        self.client = OpenAI(api_key=OPEN_AI_API_KEY)
        self.model = model  # Default model, you can override it per request

    def get_completion(self, messages, model=None, max_tokens=1500, temperature=0.2):
        """
        Get a completion from OpenAI using ChatML (messages array).

        :param messages: A list of messages in ChatML format (role-content pairs).
        :param model: The model to use (defaults to self.model if not specified).
        :param max_tokens: Maximum tokens for the response.
        :param temperature: The sampling temperature for the model.
        :return: The model's response or None if an error occurs.
        """
        # Use the specified model or the default one
        model_to_use = model or self.model
        
        try:
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
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

    def submit_answer(self, task_name, answer):
        """
        Submit an answer for a task, including API key in the payload as required.
        
        :param task_name: Identifier for the task.
        :param answer: Answer to be submitted (should be a list, not a JSON string).
        :return: API response or None if request fails.
        """
        url = f"{self.base_url}/verify"
        payload = {
            "task": task_name,
            "apikey": self.api_key,  # Include the API key directly in the payload
            "answer": answer  # Answer is sent as a JSON array, not as a string
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error in POST request to verify: {e}")
            return None





#old version of openai client

# class OpenAIClient:
#     """
#     A client to interact with OpenAI's API.
#     Provides a method to obtain completions.
#     """

#     def __init__(self, api_key):
#         """
#         Initialize the OpenAI client with an API key.

#         :param api_key: API key for OpenAI. If None, it defaults to the environment variable.
#         """
#         self.client = OpenAI(api_key=api_key)

#     def get_completion(self, prompt, model="gpt-4", max_tokens=300, temperature=0.3):
#         """
#         Get a completion response from OpenAI for a given prompt.

#         :param prompt: Text prompt for the completion.
#         :param model: OpenAI model to use.
#         :param max_tokens: Maximum tokens in the response.
#         :param temperature: Sampling temperature.
#         :return: Completion response or None if request fails.
#         """
#         messages = [{"role": "user", "content": prompt}]
#         try:
#             chat_completion = self.client.chat.completions.create(
#                 model=model,
#                 messages=messages,
#                 temperature=temperature,
#                 max_tokens=max_tokens,
#             )
#             # Accessing the message content from the response object
#             return chat_completion.choices[0].message.content
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             return None

#     def get_completion_use_tools(self, prompt, tools, model="gpt-4-1106-preview", tool_choice="auto"):
#         """
#         Create a chat completion with custom messages and tools.

#         :param messages: List of messages for the chat.
#         :param tools: List of tools to be used in the chat.
#         :param model: The OpenAI model to use.
#         :return: Chat completion response or None if request fails.
#         """
#         messages = [{"role": "user", "content": prompt}]
#         try:
#             response = self.client.chat.completions.create(
#                 model=model,
#                 messages=messages,
#                 tools=tools,
#                 tool_choice="auto",
#             )
#             return response
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             return None
        
#     def moderate_content(self, content):
#         """
#         Send content to the Moderation endpoint.

#         :param content: The content to be moderated.
#         :return: 1 if flagged, else 0.
#         """
#         try:
#             response = self.client.moderations.create(input=content)
#             flagged = int(response.results[0].flagged)
#             return flagged
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             return None

#     def get_embedding(self, text, model="text-embedding-ada-002"):
#         """
#         Get a vector embedding from OpenAI for a given text.
        
#         :param text: Text to generate embedding for.
#         :param model: OpenAI model to use for embedding.
#         :return: Embedding vector or None if request fails.
#         """
#         text = text.replace("\n", " ")
#         try:
#             response = self.client.embeddings.create(input=text, model=model)
#             # Accessing the embedding from the response object's attributes
#             return response.data[0].embedding
#         except OpenAIError as e:
#             print(f"OpenAI error: {e}")
#             return None
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             return None

#     def audio_transcription(self, file_path, model="whisper-1"):
#         """
#         Create an audio transcription using OpenAI's API.

#         :param file_path: Path to the audio file to be transcribed.
#         :param model: The OpenAI model to use for transcription.
#         :return: Transcription result or None if request fails.
#         """
#         try:
#             # Ensure the file is a PathLike instance
#             transcript = self.client.audio.transcriptions.create(model=model, file=file_path).text
#             # Accessing and returning the transcription result
#             return transcript
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             return None

#     def image_analyze(self, image_url, question, model="gpt-4-vision-preview", max_tokens=300):
#         """
#         Analyze an image using GPT-4 with Vision.

#         :param image_url: URL of the image to be analyzed.
#         :param question: Question about the image.
#         :param model: The GPT-4 model with vision capabilities.
#         :param max_tokens: Maximum tokens in the response.
#         :return: Analysis response or None if request fails.
#         """
#         messages = [
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": question},
#                     {"type": "image_url", "image_url": {"url": image_url}},
#                 ],
#             }
#         ]
#         try:
#             response = self.client.chat.completions.create(
#                 model=model,
#                 messages=messages,
#                 max_tokens=max_tokens,
#             )
#             return response.choices[0].message.content
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             return None



    