import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """
You are a helpful assistant.
Always respond in JSON format with a single key called reply.

Example:
{
  "reply": "your response here"
}
"""

# Store conversation history



def chat(user_message):
    conversation_history = []

    conversation_history.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=1024,
        response_format={
        "type": "json_object"       
    },
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            *conversation_history
        ],
    )
    

    reply_json = json.loads(response.choices[0].message.content)
    reply = reply_json["reply"]

    conversation_history.append(
        {
            "role": "assistant",
            "content": reply
        }
    )

    return reply


print("\nYour assistant is ready. Type quit to exit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        break

    response = chat(user_input)

    print(f"\nAssistant: {response}\n")