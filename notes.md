# Travel Planner - Findings

## Challenge 1 - JSON Schema Design

Schema:

destination:
- Type: string
- Stores the travel destination chosen by the user.

number_of_days:
- Type: integer
- Stores the number of days for the trip.

daily_activities:
- Type: array of objects.
- Each object represents one day and contains activities planned for that day.

estimated_budget:
- Type: number.
- Stores the estimated cost of the trip.

travel_tips:
- Type: array of strings.
- Stores practical advice for the traveler.

## Challenge 2 — Build the Planner

I built the travel planner script that asks the user for a destination and number of days, sends the request to the OpenAI API, receives a JSON response, parses it, and prints the itinerary.

### Which part of the API call enforces the schema?

The response_format parameter with type "json_schema" enforces the structure. I provided my schema.json file inside the json_schema object and enabled strict mode, which forces the model response to match the required fields and types.

### How did you connect the user's input to the prompt?

The user's destination and number of days are collected using input(). These values are inserted into the user prompt using an f-string before being sent to the API. This allows the model to generate an itinerary based on the user's requested location and trip length.

### Testing result

I tested the program with:
Destination: Cairo
Number of days: 3

The program returned valid JSON containing:
- destination
- number_of_days
- daily_activities
- estimated_budget
- travel_tips

The finish_reason returned "stop", which means the response completed normally.

## Challenge 3 — Temperature Experiments

I tested the same travel planner prompt with the same destination (Cairo) and the same number of days (3), while only changing the temperature value.

### Temperature = 0

When temperature was set to 0, the responses were the most consistent. The itinerary structure stayed the same and the activities were almost identical across the three runs. The model chose similar places, budget values, and travel tips each time.

This shows that a lower temperature makes the model more predictable and repeatable.

### Temperature = 0.5

At temperature 0.5, the responses had some variation. The JSON structure stayed exactly the same, but some activities, tips, and budget estimates changed.

For example, some runs included different Cairo attractions, different travel tips, and the estimated budget changed from around 600 to 800 or 1200.

The output was still reliable and realistic.

### Temperature = 1.2

At temperature 1.2, the responses became more creative and varied. The model generated more different itinerary ideas, different activity combinations, and different budget estimates.

However, some outputs started showing small quality issues, such as words being joined together incorrectly:
- "EgyptianMuseum"
- "NileRiver"
- "areliable"

The JSON structure was still correct and the schema was never broken.

### Observations

As temperature increased:
- Activities became more diverse.
- Travel tips changed more often.
- Budget estimates varied more.
- The creativity increased, but the output became slightly less consistent.

The JSON schema did not break because temperature only affects how the model chooses content. The response format is controlled separately by the JSON schema enforcement, so the model still had to follow the required structure.

### Conclusion

For a real travel planner, a medium temperature would be better because it gives some creativity while keeping the output reliable. A value around 0.5-0.7 would provide variety without causing strange or inconsistent results.

## Challenge 4 — Max Tokens Experiments

The temperature is kept fixed at 0.7 and changed only the max_tokens value.

### max_tokens = 50

With a very low max_tokens value, the model could not generate the complete JSON response. The response was cut off before finishing, which caused the JSON to be incomplete.

At first, this caused a JSONDecodeError because the program tried to parse incomplete JSON. I added a try/except block to handle this situation and display a message instead of crashing.

The output showed:

Finish reason: length

This means the model stopped because it reached the maximum token limit before completing the response.

### max_tokens = 500

With a medium max_tokens value, the model generated a complete travel itinerary. All required fields were included and the JSON schema remained valid.

The output finished with:

Finish reason: stop

This means the model completed the response naturally.

### max_tokens = 2000

With a high max_tokens value, the response was also completed successfully.

The output finished with:

Finish reason: stop

Increasing max_tokens beyond what the response needs did not significantly change the output because the model finished before reaching the limit.

### Observations

max_tokens controls the maximum length of the model response. A token is a unit of text processed by the model. The number of tokens determines how much content the model can generate before stopping.

A low max_tokens value can cause incomplete responses, especially when generating structured JSON. A higher value gives the model enough space to finish, but setting it unnecessarily high can increase cost.

For a real application, I would choose a max_tokens value based on the expected response size and leave enough room to avoid truncation.

## Final Recommendation

For the Travel Planner application, I chose:

temperature = 0.7

max_tokens = 700

I chose temperature 0.7 because it gave the best balance between creativity and reliability. At temperature 0, the responses were very consistent but almost identical each time. At temperature 1.2, the responses had more variety, but sometimes the text quality decreased with formatting issues and unusual wording. Temperature 0.7 produced different travel ideas while keeping the JSON structure valid.

I chose max_tokens 700 because it provides more room than 500 while avoiding the unnecessarily high limit of 2000. Testing showed that short itineraries completed successfully, while longer itineraries may require a higher value. During testing, max_tokens=50 caused incomplete JSON responses and finish_reason was "length". Values like 500 and 2000 completed successfully for short trips, but 700 provides extra room while still being efficient.

I also tested a longer trip (UAE for 60 days) with max_tokens=700 and the response was incomplete because the itinerary was much larger than a normal request. This showed that max_tokens should be adjusted depending on the expected response size.

The best production combination is temperature 0.7 and max_tokens 700 because it creates creative, complete, and reliable travel plans while controlling token usage.

If users complain that all itineraries look the same, I would increase temperature to create more variation.

If users complain that responses are cut off, I would increase max_tokens to allow longer responses.