import requests
from utilities.common import OpenAIClient
from utilities.config import S01E02_TASK_URL

client_openai = OpenAIClient()
base_url = S01E02_TASK_URL

def initiate_verification():
    try:
        response = requests.post(base_url, json={"text": "READY", "msgID": "0"})
        response.raise_for_status()
        robot_reply = response.json()
        print("Robot's Question:", robot_reply.get("text"))
        return robot_reply.get("msgID"), robot_reply.get("text")
    except requests.RequestException as e:
        print(f"Error communicating with the robot: {e}")
        return None, None

def respond_to_robot(msgID, question_text):
    messages = [
        {"role": "system", "content": (
            "You are a helpful assistant that answers questions in English, following specific rules. "
            "If asked about the capital of Poland, respond 'CRACOW'. "
            "If asked about the famous number from 'The Hitchhiker's Guide to the Galaxy', respond '69'. "
            "If asked about the current year, respond '1999'. For all other questions, respond with the accurate answer."
        )},
        {"role": "user", "content": question_text}
    ]

    try:
        answer = client_openai.get_completion(messages=messages, model="gpt-4o-mini", temperature=0.1)
        print("Question:", question_text, "| Answer:", answer)
    except Exception as e:
        print(f"Error generating answer: {e}")
        return

    response_message = {"text": answer, "msgID": msgID}
    try:
        response = requests.post(base_url, json=response_message)
        response.raise_for_status()
        final_reply = response.json()
        flag = final_reply.get("text")
        if flag and "FLG" in flag:
            print("Verification Successful! FLAG:", flag)
        else:
            print("Verification failed or FLAG not provided.")
    except requests.RequestException as e:
        print(f"Error sending response to robot: {e}")

if __name__ == "__main__":
    msgID, question_text = initiate_verification()
    if msgID and question_text:
        respond_to_robot(msgID, question_text)
