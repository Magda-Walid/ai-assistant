from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("story.txt", "r", encoding="utf-8") as file:
    story = file.read()


question = "Who gave Mattias the compass and why?"


response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": f"""
You are answering questions about this story:

{story}

Answer only using the story.
"""
        },
        {
            "role": "user",
            "content": question
        }
    ]
)


print(response.choices[0].message.content)