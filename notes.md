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

The travel planner script asks the user for a destination and number of days, sends the request to the OpenAI API, receives a JSON response, parses it, and prints the itinerary.

### Which part of the API call enforces the schema?

The `response_format` parameter with type `"json_schema"` enforces the structure. The `schema.json` file is provided inside the `json_schema` object and strict mode is enabled, which forces the model response to match the required fields and data types.

### How was the user's input connected to the prompt?

The user's destination and number of days are collected using `input()`. These values are inserted into the user prompt using an f-string before being sent to the API. This allows the model to generate an itinerary based on the requested location and trip length.

### Testing result

Test input:

Destination: Cairo  
Number of days: 3

The program returned valid JSON containing:
- destination
- number_of_days
- daily_activities
- estimated_budget
- travel_tips

The finish_reason returned `"stop"`, which means the response completed normally.


# Challenge 3 — Temperature Experiments

The same travel planner prompt was tested with the same destination (Cairo) and number of days (3), while only changing the temperature value.

## Temperature = 0

When temperature was set to 0, the responses were the most consistent. The itinerary structure stayed the same and the activities were almost identical across the three runs. The model selected similar places, budget values, and travel tips each time.

This shows that a lower temperature makes the model more predictable and repeatable.

## Temperature = 0.5

At temperature 0.5, the responses had some variation. The JSON structure stayed exactly the same, but some activities, tips, and budget estimates changed.

For example, some runs included different Cairo attractions, different travel tips, and estimated budgets changed from around 600 to 800 or 1200.

The output was still reliable and realistic.

## Temperature = 1.2

At temperature 1.2, the responses became more creative and varied. The model generated more different itinerary ideas, different activity combinations, and different budget estimates.

However, some outputs started showing small quality issues, such as words being joined together incorrectly:

- "EgyptianMuseum"
- "NileRiver"
- "areliable"

The JSON structure was still correct and the schema was never broken.

## Observations

As temperature increased:

- Activities became more diverse.
- Travel tips changed more often.
- Budget estimates varied more.
- Creativity increased, but output consistency decreased.

The JSON schema did not break because temperature only affects how the model selects content. The response format is controlled separately by JSON schema enforcement, so the model still had to follow the required structure.

## Conclusion

For a real travel planner, a medium temperature is better because it gives creativity while keeping the output reliable. A value around 0.5-0.7 provides variety without causing strange or inconsistent wording.


# Challenge 4 — Max Tokens Experiments

The temperature was kept fixed at 0.7 and only the `max_tokens` value was changed.

## max_tokens = 50

With a very low max_tokens value, the model could not generate the complete JSON response. The response was cut off before finishing, which caused incomplete JSON.

At first, this caused a JSONDecodeError because the program attempted to parse incomplete JSON. A try/except block was added to handle this situation and display a message instead of crashing.

The output showed:

Finish reason: length

This means the model stopped because it reached the maximum token limit before completing the response.

## max_tokens = 500

With a medium max_tokens value, the model generated a complete travel itinerary. All required fields were included and the JSON schema remained valid.

The output finished with:

Finish reason: stop

This means the model completed the response naturally.

## max_tokens = 2000

With a high max_tokens value, the response was also completed successfully.

The output finished with:

Finish reason: stop

Increasing max_tokens beyond what the response needed did not significantly change the output because the model finished before reaching the limit.

## Observations

`max_tokens` controls the maximum amount of text the model can generate. A token is a unit of text processed by the model.

A low max_tokens value can cause incomplete responses, especially when generating structured JSON. A higher value gives the model enough space to finish, but setting it unnecessarily high can increase cost.

For a real application, max_tokens should be selected based on the expected response size while leaving enough space to avoid truncation.


# Final Recommendation

For the Travel Planner application:

temperature = 0.7

max_tokens = 700

Temperature 0.7 was selected because it gave the best balance between creativity and reliability. At temperature 0, the responses were very consistent but almost identical. At temperature 1.2, the responses had more variety but sometimes had formatting and wording issues. Temperature 0.7 produced different travel ideas while keeping the JSON structure valid.

max_tokens 700 was selected because it provides more space than 500 while avoiding unnecessary token usage like 2000. Testing showed that max_tokens=50 caused incomplete JSON responses with finish_reason `"length"`. Values like 500 and 2000 completed successfully for short trips, but 700 provides extra room while remaining efficient.

A longer trip test (UAE for 60 days) with max_tokens=700 produced an incomplete response because the itinerary was much larger than a normal request. This showed that max_tokens should depend on the expected response size.

The best production combination is temperature 0.7 and max_tokens 700 because it creates creative, complete, and reliable travel plans while controlling token usage.

If users complain that all itineraries look the same, increasing temperature can create more variation.

If users complain that responses are cut off, increasing max_tokens can allow longer responses.


# Task 5 — Challenge 1: Validate User Input

## Validation Rules

For the destination field:

- The destination cannot be empty or contain only spaces.
- The destination cannot be only numbers.
- The destination must contain a valid name.

For the number of days field:

- The input must be an integer.
- The number of days must be between 1 and 21.
- The maximum limit prevents extremely large itinerary requests that could create very long responses and increase the chance of reaching the token limit.

## Before This Challenge

Before adding validation, entering a non-number value for days (for example: `"abc"`) caused the program to crash.

The error happened during integer conversion:


days = int(input("Enter number of days: "))

# Task 5 — Challenge 2: Don't Trust Valid JSON Either

## Approach Used

A manual validation function called `validate_itinerary(data)` was added to check that the parsed JSON response matches the expected travel schema.

Manual validation was chosen because the project only contains five main fields, so simple type and structure checks are enough. This keeps the script lightweight and avoids adding unnecessary dependencies.

The function raises a clear `ValueError` when the AI response does not match the expected structure.

## Validation Rules

The function checks the following fields:

### destination

- The field must exist.
- The value must be a string.

### number_of_days

- The field must exist.
- The value must be an integer.

### daily_activities

- The field must exist.
- The value must be a list.
- Each item inside the list must be an object/dictionary.
- The list cannot be empty.

### estimated_budget

- The field must exist.
- The value must be a number (integer or float).

### travel_tips

- The field must exist.
- The value must be a list.
- Each item must be a string.
- The list cannot be empty.

## Broken Test Case

A manual broken test case was created to test the validation function:


bad_test = {
    "destination": "Cairo",
    "number_of_days": "three",
    "daily_activities": [],
    "estimated_budget": "around $800",
    "travel_tips": ["Stay hydrated"]
}



# Task 5 — Challenge 3: Handle API Errors

## API Error Handling

The OpenAI API call was wrapped with exception handling to prevent the program from crashing when the API request fails.

Different exception types were handled separately because each type of failure requires a different response.

## Handled Exception Types

### AuthenticationError

Triggered by changing the API key in the `.env` file to an invalid value.

Before:
- The program crashed with an OpenAI authentication error traceback.

After:
- The program displays a clear authentication error message and stops safely.

### RateLimitError

Handled because rate limits are usually temporary.

The program retries automatically a limited number of times with a waiting period between attempts.

If all retries fail, a clear message is shown to the user.

### APIConnectionError

Handled because network problems or connection interruptions can happen temporarily.

The program retries the API request a limited number of times before displaying a connection error message.

### BadRequestError

Handled because invalid requests cannot be fixed by retrying.

The program displays a clear message explaining that the request was invalid instead of showing a raw traceback.

## Testing and Observations

The authentication error was deliberately triggered by using an invalid API key.

Before adding error handling:
- The program stopped with an unhandled exception.

After adding error handling:
- The program catches the error and displays a user-friendly message.

Rate limit and connection errors were handled in the code with retry logic because they can happen temporarily and may succeed later.

## Conclusion

API errors should not all be handled the same way.

Temporary failures such as rate limits and connection issues can be retried.

Permanent failures such as invalid API keys or bad requests should stop immediately and provide a clear explanation.

# Task 5 — Challenge 4: Decide What Deserves a Retry

## Retry Policy

The retry policy depends on the type of failure because not every error can be fixed by trying again.

### AuthenticationError

- Automatic retry: No.
- Reason: An invalid or expired API key will fail every time until the key is fixed.
- Action: Show a clear error message asking the user to check the API key.

### RateLimitError

- Automatic retry: Yes.
- Retry count: Maximum 3 attempts.
- Reason: Rate limits are usually temporary and another request may succeed later.
- Action: Wait between attempts using a delay before retrying.
- If all retries fail, show a message asking the user to try again later.

### APIConnectionError

- Automatic retry: Yes.
- Retry count: Maximum 3 attempts.
- Reason: Network problems can be temporary.
- Action: Retry after a short delay.
- If all retries fail, display a connection error message.

### BadRequestError

- Automatic retry: No.
- Reason: The request itself is invalid, so sending the same request again will not solve the problem.
- Action: Show a clear message explaining that the request was rejected.

### Invalid User Input

- Automatic retry: No API retry.
- Reason: Invalid input must be corrected by the user.
- Action: Keep asking the user until valid input is entered.

### Invalid JSON Response

- Automatic retry: No.
- Reason: The response cannot be trusted if it is incomplete or malformed.
- Action: Display an error message instead of printing invalid data.

### Schema Validation Failure

- Automatic retry: No.
- Reason: The returned data does not match the expected structure.
- Action: Reject the response and prevent invalid data from reaching the user.

## Retry Adjustment

If users complain that the application hangs because it retries too much, the first parameter to adjust would be the retry count or the waiting time between retries.

If users complain that the application gives up too quickly, the first parameter to adjust would be increasing the retry count or improving the backoff delay.

A limited retry policy is important because unlimited retries can waste time, increase API costs, and create a bad user experience.