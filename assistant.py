import os
import json
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
Always respond in JSON format with a single key called reply.
Example:
{
  "reply": "your response here"
}
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
        model="gpt-4o-mini",
        max_tokens=1024,
        response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "assistant_response",
            "schema": {
                "type": "object",
                "properties": {
                    "reply": {
                        "type": "string"
                    }
                },
                "required": ["reply"],
                "additionalProperties": False
            }
        }
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
    print(reply_json)
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