from pandas import DataFrame
from config import *
from app.data_models import MessageInput



def prepare_few_shot_prompt(data, few_shot_limit):
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
        reference_messages += f"Message {index+1}\n{message}\n\n"
        few_shot_prompt += f'\nExample {index + 1}:\n### Signal: "{signal}"\n### Signal-Category: {category}\n### Sender: {sender}\n### Receiver: {receiver}\n### Message: "{message}" \n'
    
    return few_shot_prompt, reference_messages


def generate_message_with_openai(reference_data: DataFrame, message_input: MessageInput, few_shot_limit:int = FEW_SHOT_LIMIT) -> str:

    sender = message_input.sender
    receiver = message_input.receiver
    category = message_input.category
    signal = message_input.signal
    
    few_shot_examples, reference_messages = prepare_few_shot_prompt(reference_data,few_shot_limit=few_shot_limit)
    sys_prompt = f"""
You are an AI assistant that creates professional, personalized email messages in English.
Your task is to EXACTLY mimic the style, tone, and structure provided in historical messages. 
The messages were written by a specific sender to reach its Receiver with personalized message curated using information from SIGNAL and the intent of message is inferred from SIGNAL-CATEGORY.
Hence, the new generated message should incorporate new SIGNAL as a context and style should be suitable for the Signal-Category.

CRITICAL INSTRUCTIONS:
1. Stick to ONLY the style and structure of the historical messages.
2. Infer the length and number of paragraphs from historical messages and Signal-Category
3. Do NOT introduce any new ideas or concepts not present in the Signal message.
4. ALWAYS start with the same greeting style and end with the same closing style as the historical message.

Historical message to mimic:
{few_shot_examples}

Follow this sample when composing the new message and make sure that both the SIGNAL and SIGNAL-Category are appropriately reflected in the message content, length and style.    
"""
    user_prompt = f"""
Based on the information provided, generate a new email in English.
The message must match the style and tone of the examples above and take appropriate account of the category, even if the sender or recipient are different.

New task:
### Signal: {signal}
### Signal-Category: {category}
### Sender: {sender}
### Receiver: {receiver}

### Message:
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

