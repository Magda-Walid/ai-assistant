from openai import OpenAI
import json
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI()

with open("schema.json", "r") as file:
    travel_schema = json.load(file)


def get_user_input():
    destination = input("Enter destination: ")
    days = int(input("Enter number of days: "))

    return destination, days


def create_prompt(destination, days):
    prompt = f"""
        Create a travel itinerary.

        Destination: {destination}
        Number of days: {days}

        Return only the JSON structure requested.
        """

    return prompt


def main():

    destination, days = get_user_input()

    prompt = create_prompt(destination, days)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=700,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "travel_itinerary",
                "schema": travel_schema,
                "strict": True
            }
        },
        messages=[
            {
                "role": "system",
                "content": "You are a travel planner that creates structured JSON itineraries."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    raw_json = response.choices[0].message.content
    print("\nRaw response:")
    print(raw_json)
    try:
        itinerary = json.loads(raw_json)
    except json.JSONDecodeError:
        print("The response was incomplete because max_tokens was too low.")
        print("Finish reason:", response.choices[0].finish_reason)
        return


    print("\n--- Travel Plan ---")

    print("Destination:", itinerary["destination"])
    print("Days:", itinerary["number_of_days"])

    print("\nActivities:")
    for day in itinerary["daily_activities"]:
        print(day)

    print("\nBudget:", itinerary["estimated_budget"])

    print("\nTips:")
    for tip in itinerary["travel_tips"]:
        print("-", tip)


    print("\nFinish reason:")
    print(response.choices[0].finish_reason)


if __name__ == "__main__":
    main()