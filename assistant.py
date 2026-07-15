import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Your assistant personality
SYSTEM_PROMPT = """
You are a friendly AI programming tutor.
You explain Python and AI concepts clearly for beginners.
You speak in a helpful and encouraging way.
"""

# Store conversation history
conversation_history = []


def chat(user_message):

    conversation_history.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=200,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
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