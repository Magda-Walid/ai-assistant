import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

# Initialize environment variables
load_dotenv()

# Retrieve API credentials from environment
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate required environment variables
if not OPENWEATHER_API_KEY:
    raise ValueError("OPENWEATHER_API_KEY is missing in .env file")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing in .env file")

# Configure the OpenAI API client
client = OpenAI(api_key=OPENAI_API_KEY)


def get_weather(city: str, unit: str = "celsius") -> dict:
    # Retrieve geographic coordinates for the specified city
    geo_url = "https://api.openweathermap.org/geo/1.0/direct"
    geo_params = {"q": city, "limit": 1, "appid": OPENWEATHER_API_KEY}
    geo_response = requests.get(geo_url, params=geo_params)
    geo_data = geo_response.json()

    # Validate geolocation response
    if not isinstance(geo_data, list) or len(geo_data) == 0:
        return {"error": f"City '{city}' not found"}

    lat = geo_data[0]["lat"]
    lon = geo_data[0]["lon"]

    # Fetch weather data based on coordinates
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    weather_params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    weather_response = requests.get(weather_url, params=weather_params)
    weather_data = weather_response.json()

    # Check for API errors
    if weather_data.get("cod") != 200:
        return {"error": weather_data.get("message", "Unknown error")}

    # Process temperature data and handle unit conversion
    temp = weather_data["main"]["temp"]
    if unit == "fahrenheit":
        temp = temp * 9/5 + 32

    # Format and return weather results
    return {
        "city": city,
        "temperature": round(temp, 2),
        "unit": unit,
        "condition": weather_data["weather"][0]["description"],
        "humidity": weather_data["main"]["humidity"]
    }


# Define tools available to the assistant
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a given city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. Cairo"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["city"]
        }
    }
}]


# Configure system instruction for the assistant
system_prompt = {
    "role": "system",
    "content": "You are a helpful weather assistant. Only answer weather-related questions. "
               "If the user gives a city name after you asked for one, treat it as the city for weather."
}

messages = [system_prompt]
waiting_for_city = False

while True:
    user_input = input("User: ").strip()
    if user_input.lower() in ["exit", "quit", "bye"]:
        break
    if not user_input:
        continue

    
    # Use a secondary model to classify user intent and extract parameters
    classification_messages = [
        {
            "role": "system",
            "content": """
You classify weather requests.

Rules:
- is_weather=true if the user asks about weather, temperature, conditions, etc.
- Extract city if clearly mentioned.
- If the user asks about weather but does not provide a city, set needs_city=true.
- If previous assistant asked for a city and the user only writes a city name (or very short phrase), treat it as providing the city.
"""
        },
        {"role": "user", "content": user_input}
    ]

    try:
        classification = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=classification_messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "weather_classifier",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "is_weather": {"type": "boolean"},
                            "city": {"type": ["string", "null"]},
                            "unit": {"type": ["string", "null"], "enum": ["celsius", "fahrenheit", None]},
                            "needs_city": {"type": "boolean"}
                        },
                        "required": ["is_weather", "city", "unit", "needs_city"],
                        "additionalProperties": False
                    }
                }
            }
        )

        data = json.loads(classification.choices[0].message.content)
    except Exception as e:
        # Handle parsing errors gracefully
        print("AI: Sorry, I had trouble understanding that.")
        continue

    # Filter requests unrelated to weather
    if not data.get("is_weather"):
        print("AI: I'm sorry, I can only provide weather information.")
        continue

    #Handle city request 
    # Manage states where the city information is missing
    if waiting_for_city or data.get("needs_city"):
        city_to_use = data.get("city") if data.get("city") and data.get("city").strip() else user_input

        messages.append({"role": "user", "content": f"What's the weather in {city_to_use}?"})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools
        )
        msg = response.choices[0].message

        # Process tool calls if requested by the model
        if msg.tool_calls:
            messages.append(msg)
            for call in msg.tool_calls:
                args = json.loads(call.function.arguments)
                if data.get("unit") is not None:
                    args["unit"] = data["unit"]

                result = get_weather(**args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result)
                })

            # Retrieve final response after tool execution
            final = client.chat.completions.create(model="gpt-4o", messages=messages)
            print("AI:", final.choices[0].message.content)
            messages.append(final.choices[0].message)
        else:
            # Handle standard text responses
            print("AI:", msg.content)
            messages.append(msg)

        waiting_for_city = False
        continue

    # Normal flow 
    # Standard interaction path for fully qualified queries
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools
    )

    msg = response.choices[0].message

    # Execute and handle tool calls for standard requests
    if msg.tool_calls:
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            if data.get("unit") is not None:
                args["unit"] = data["unit"]

            result = get_weather(**args)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result)
            })

        final = client.chat.completions.create(model="gpt-4o", messages=messages)
        print("AI:", final.choices[0].message.content)
        messages.append(final.choices[0].message)
    else:
        # Handle non-tool conversational responses
        print("AI:", msg.content)
        messages.append(msg)

    waiting_for_city = data.get("needs_city", False)