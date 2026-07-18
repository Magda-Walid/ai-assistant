from openai import OpenAI, APIError, AuthenticationError, RateLimitError, APIConnectionError, BadRequestError
import json
from dotenv import load_dotenv
import os


load_dotenv()

client = None

def get_client():
    global client
    
    if client is None:
        client = OpenAI()
    
    return client

with open("schema.json", "r") as file:
    travel_schema = json.load(file)


def get_user_input():
    # Validate Destination
    while True:
        destination = input("Enter destination: ").strip()
        
        if not destination:
            print("Destination cannot be empty. Please try again.")
            continue
        
        if destination.isdigit() or len(destination) < 2:
            print("Please enter a valid destination name (not just numbers).")
            continue
        
        break

    # Validate Number of Days
    while True:
        try:
            days_input = input("Enter number of days: ").strip()
            days = int(days_input)
            
            if days < 1:
                print("Number of days must be at least 1.")
                continue
            elif days > 21:   #(prevents huge token usage)
                print("Number of days must be between 1 and 21.")
                continue
            
            return destination, days
            
        except ValueError:
            print("Please enter a valid number for days.")
            continue


def validate_itinerary(data):
    
    if not isinstance(data, dict):
        raise ValueError("Invalid response: Expected a JSON object (dictionary).")

    # Check required fields
    required_fields = ["destination", "number_of_days", "daily_activities", 
                      "estimated_budget", "travel_tips"]
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: '{field}'")

    # Type validation
    if not isinstance(data["destination"], str):
        raise ValueError("Invalid type: 'destination' should be a string.")
    
    if not isinstance(data["number_of_days"], int):
        raise ValueError("Invalid type: 'number_of_days' should be an integer.")
    
    if not isinstance(data["daily_activities"], list):
        raise ValueError("Invalid type: 'daily_activities' should be a list.")
    
    for tip in data["travel_tips"]:
        if not isinstance(tip, str):
            raise ValueError("Each travel tip should be a string.")
    
    for day in data["daily_activities"]:
        if not isinstance(day, dict):
            raise ValueError("Each daily activity should be an object.")
    
    if len(data["travel_tips"]) == 0:
        raise ValueError("'travel_tips' list cannot be empty.")
    if len(data["daily_activities"]) == 0:
        raise ValueError("'daily_activities' list cannot be empty.")
    
    
    budget = data["estimated_budget"]

    if not isinstance(budget, (int, float)):
        raise ValueError("'estimated_budget' should be a number.")
        
    return True  # Validation passed


def call_openai_with_retry(prompt, max_retries=3):
    
    for attempt in range(max_retries):
        try:
            response = get_client().chat.completions.create(
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
            return response

        except AuthenticationError:
            print("Authentication Error: Your OpenAI API key is invalid or expired.")
            print("Please check your .env file and ensure OPENAI_API_KEY is correct.")
            raise # Don't retry auth errors

        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # simple backoff
                print(f"Rate limit hit. Waiting {wait_time} seconds before retry")
                import time
                time.sleep(wait_time)
                continue
            else:
                print("Rate limit exceeded. Please try again later.")
                raise

        except APIConnectionError:
            if attempt < max_retries - 1:
                print(f"Connection error. Retrying ({attempt+1}/{max_retries})")
                import time
                time.sleep(1)
                continue
            else:
                print("Could not connect to OpenAI. Check your internet connection.")
                raise

        except BadRequestError as e:
            print(f"Bad Request: {str(e)}")
            raise

        except APIError as e:
            print(f"OpenAI API Error: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying ({attempt+1}/{max_retries})...")
                import time
                time.sleep(2)
                continue
            raise

        except Exception as e:  # Catch any other unexpected errors
            print(f"Unexpected error: {str(e)}")
            raise
def create_prompt(destination, days):
    prompt = f"""
        Create a travel itinerary.

        Destination: {destination}
        Number of days: {days}

        Return only the JSON structure requested.
        """

    return prompt

#test for challenge 2
#bad_test = {
#    "destination": "Cairo",
 #   "number_of_days": "three",
  #  "daily_activities": [],
   # "estimated_budget": "around $800",
    #"travel_tips": ["Stay hydrated"]
#}

#validate_itinerary(bad_test)


def main():
    destination, days = get_user_input()

    prompt = create_prompt(destination, days)

    print("\nGenerating your travel itinerary...")

    try:
        response = call_openai_with_retry(prompt)

    except AuthenticationError:
            print("\nAuthentication failed. Please check your API key.")
            return

    except RateLimitError:
            print("\nToo many requests. Please try again later.")
            return

    except APIConnectionError:
            print("\nConnection problem. Check your internet connection.")
            return

    except BadRequestError:
            print("\nThe request sent to OpenAI was invalid.")
            return

    except Exception as e:
            print("\nUnexpected error occurred:")
            print(e)
            return

    raw_json = response.choices[0].message.content
    print("\nRaw response:")
    print(raw_json)

    try:
        itinerary = json.loads(raw_json)
    except json.JSONDecodeError:
        print("The response was incomplete or invalid JSON.")
        print("Finish reason:", response.choices[0].finish_reason)
        return

    try:
        validate_itinerary(itinerary)
        print("Itinerary validation passed.")
    except ValueError as e:
        print(f"Validation failed: {e}")
        return

    # Print the itinerary
    print("\n--- Travel Plan ---")
    print("Destination:", itinerary["destination"])
    print("Days:", itinerary["number_of_days"])

    print("\nActivities:")
    for day in itinerary["daily_activities"]:
        print(f"- {day}")

    print("\nBudget:", itinerary["estimated_budget"])

    print("\nTips:")
    for tip in itinerary["travel_tips"]:
        print(f"- {tip}")

    print("\nFinish reason:")
    print(response.choices[0].finish_reason)


if __name__ == "__main__":
    main()