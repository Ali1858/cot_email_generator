import os

import pandas as pd
from pandas import DataFrame
from openai import OpenAI
from config import *
from app.data_models import MessageInput
from dotenv import load_dotenv

load_dotenv()
# Initialize OpenAI API
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def load_csv_data(file_name=SAMPLE_CSV):
    # Load the sample data
    return pd.read_csv(file_name)


def get_sender_data(df, sender: str, category: str) -> list:
    # Filter data for the specific sender and category
    data = df[(df['Sender'] == sender) & (df["Category"] == category)]
    
    if data.empty:
        return None
    return data


def get_best_sender_name(df):
    " Randomly send sender name with best messages (best saleman)"
    # Ideally we can send best salesman name
    return df['Sender'].sample().iloc[0]


def prepare_few_shot_prompt_cot(data, few_shot_limit):
    "Concat signal, its category and message into one string for few-shot prompt"

    examples = data.head(min(few_shot_limit, len(data))).reset_index()
    reference_messages = ""
    few_shot_prompt = ""

    for index, row in examples.iterrows():
        signal = row['Signal']
        category = row['Category']
        message = row['Message']
        sender = row['Sender']
        receiver = row['Receiver']
        signal_brief = row["signal_brief"]
        category_brief = row["category_brief"]
        message_key_point = row["message_key_point"]
        reference_messages += f"Message {index+1}\n{message}\n\n"
        few_shot_prompt += f'''
Example {index + 1}:
### Signal: "{signal}"
### Signal-Category: {category}
### Sender: {sender}
### Receiver: {receiver}
 
# Thought process:
# 1. Analyze the signal: The signal provides context for {signal_brief}.
# 2. Consider the category: The category suggests {category_brief}.
# 3. Identify key points to address in Signal based on intent of Category: Based on the signal and intent category, the key points to address are {message_key_point}.
# 4. Write the message: Consider Singal, Category, Signal Key points and write the message

### Message: "{message}"
'''
    return few_shot_prompt, reference_messages


def generate_message_with_openai_cot(reference_data: DataFrame, message_input: MessageInput, few_shot_limit:int = FEW_SHOT_LIMIT) -> str:

    sender = message_input.sender
    receiver = message_input.receiver
    category = message_input.category
    signal = message_input.signal
    
    few_shot_examples, reference_messages = prepare_few_shot_prompt_cot(reference_data,few_shot_limit=few_shot_limit)
    sys_prompt = f"""
You are an AI assistant that creates professional, personalized email messages in German. Your task is to EXACTLY mimic the style, tone, and structure provided in historical messages, while explaining your though process.

The messages were written by a specific sender to reach its Receiver with personalized message curated using information from SIGNAL and the intent of message is inferred from SIGNAL-CATEGORY. Hence, the new generated message should incorporate new SIGNAL as a context and style should be suitable for the Signal-Category.

CRITICAL INSTRUCTIONS:
1. Stick to ONLY the style and structure of the historical messages.
2. Infer the length and number of paragraphs from historical messages and Signal-Category
3. Do NOT introduce any new ideas or concepts not present in the Signal message.
4. ALWAYS start with the same greeting style and end with the same closing style as the historical message.
5. Explain your thought process for each step of message creation.

Historical message to mimic (including thought processes):
{few_shot_examples}

Follow this sample when composing the new message and make sure that both the SIGNAL and SIGNAL-Category are appropriately reflected in the message content, length and style.    
"""
    user_prompt = f"""
    Based on the information provided, generate a new email in German.
The message must match the style and tone of the examples above and take appropriate account of the category, even if the sender or recipient are different. Explain your reasoning at each step.

New task:
### Signal: {signal}
### Signal-Category: {category}
### Sender: {sender}
### Receiver: {receiver}

Please think through the email generation process step-by-step:
1. Analyze the signal: 
2. Consider the category: 
3. Identify key points to address in Signal based on intent of Category: 
4. Write the message: 

### Thought Process:
[Your step-by-step reasoning here]

### Message:
[Your generated email here]
"""

    response = client.chat.completions.create(
        model=OPEN_AI_MODEL_NAME,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=MAX_TOKEN,
        n=1,
        temperature=TEMP,
    )

    return response.choices[0].message.content.strip(), reference_messages
