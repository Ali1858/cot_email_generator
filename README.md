# Chain of Thought: Personalized Message Generation API

## Objective
This project implements a FastAPI-based application that generates personalized messages mimicking the style, tone, and structure of specific users. It uses OpenAI's GPT model model to create context-aware messages based on historical data and new input signals.

The main goals of this API are:
1. Use Chain of Thought to analyze input contex/signal and intent category to generated key point a message should address.
2. Incorporate new context (signals) into the generated messages.
3. Generate messages according to the key point and historical messages.

Chain of thought example:
```text
# Thought process:
# 1. Analyze the signal: The signal provides context for {signal_brief}.
# 2. Consider the category: The category suggests {category_brief}.
# 3. Identify key points to address in Signal based on intent of Category: Based on the signal and intent category, the key points to address are {message_key_point}.
# 4. Write the message: Consider Singal, Category, Signal Key points and write the message

### Message: "{message}"

```
## API Details

### Endpoint

`POST /generate_message`

This endpoint generates a new message based on the provided input.

### Input Schema

The API accepts the following JSON input:

```json
{
  "sender": "string",
  "receiver": "string",
  "category": "string",
  "signal": "string",
  "generate_from_best": "boolean (optional, default: false), when samples are not available for the given sender"
}
```

- `sender`: The name of the user who composed the message.
- `receiver`: The name of the user who receives the message.
- `category`: The detected signal category.
- `signal`: The content of the signal.
- `generate_from_best`: If true, the API will use a (ideally best) random user's data when the specified sender is not found.

### Output Schema

The API returns the following JSON output:

```json
{
  "message_body": "string",
  "reference_message": "string (optional)",
  "status": "string (optional)"
}
```

- `message_body`: The generated message.
- `reference_message`: A sample message used as a reference for generation.
- `status`: The status of the message generation process.


## Setup and Running

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set OpenAI API key:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```

3. Ensure that the `sample_data.csv` file is present in the project `data` directory.

4. Run the FastAPI application:
   ```
   python main.py
   ```

   The API will be available at `http://localhost:8000`.

5. You can interact with the API using the Swagger UI at `http://localhost:8000/docs`.
