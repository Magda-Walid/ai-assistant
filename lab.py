import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a helpful assistant.
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
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": "apple"
            },
            {
                "role": "assistant",
                "content": "apple :: noun :: a round fruit that grows on trees :: fruit"
            },
            {
                "role": "user",
                "content": "river"
            },
            {
                "role": "assistant",
                "content": "river :: noun :: a large natural stream of water :: nature"
            },
            *conversation_history
        ],
    )
    

    reply = response.choices[0].message.content

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