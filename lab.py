import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a friendly computer science teacher.
Always create clear educational flashcards.
"""





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
        max_tokens=100,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": "Python"
            },
            {
                "role": "assistant",
                "content": "Python :: Programming Language :: A language used to build software and automate tasks :: Computer Science"
            },
            {
                "role": "user",
                "content": "Database"
            },
            {
                "role": "assistant",
                "content": "Database :: Storage System :: A place where information is organized and stored for easy access :: Computer Science"
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
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