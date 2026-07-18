from dotenv import load_dotenv
import os
import json
import chromadb

from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


with open("story.txt", "r", encoding="utf-8") as file:
    story = file.read()


def split_story(story):
    chunks = [chunk for chunk in story.split("\n\n") if chunk.strip()]
    return chunks


chunks = split_story(story)
print("Total number of chunks:", len(chunks))

chroma_client = chromadb.Client()
collection=chroma_client.create_collection(name="story_collection")


def create_embeddings(chunks):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )

    return [item.embedding for item in response.data]


embeddings = create_embeddings(chunks)

collection.add(
    ids=[str(i) for i in range(len(chunks))],
    documents=chunks,
    embeddings=embeddings
)

def search_story(question):

    question_embedding = create_embeddings([question])[0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=5
    )

    return [
        {
            "chunk": chunk
        }
        for chunk in results["documents"][0]
    ]

def search_story(question):

    question_embedding = create_embeddings([question])[0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=5
    )

    return [
        {
            "chunk": chunk
        }
        for chunk in results["documents"][0]
    ]

tools=[
    {
        "type":"function",
        "function":{
            "name":"search_story",
            "description":"Searches the story for relevant chunks based on a question.",
            "parameters":{
                "type":"object",
                "properties":{
                    "question":{
                        "type":"string",
                        "description":"The user's question about the story"
                    }
                },
                "required":["question"]
            }
        }
    }
]
question=input("Ask a question about the story: ")
response=client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role":"system",
            "content": "You answer questions only about the provided story. Always use the search_story tool before answering. Do not use your general knowledge."

        },
        {
            "role":"user",
            "content":question
        }
    ],
    tools=tools
)
message=response.choices[0].message
if message.tool_calls:
    tool_call=message.tool_calls[0]
    arguments=json.loads(tool_call.function.arguments)
    results=search_story(arguments["question"])

    context="\n\n".join([result["chunk"] for result in results])
    final_response=client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role":"system",
                "content":
                "Answer only using the provided story context. Combine information from multiple chunks when necessary. If the answer is not in the context, say I don't know."
            },
            {
                "role":"user",
                "content":
                f"Context:\n{context}\n\nQuestion: {question}"
            }
        ]
    )

    print(final_response.choices[0].message.content)


else:
    print(message.content)