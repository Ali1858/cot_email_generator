from fastapi import FastAPI, HTTPException

from app.data_models import *
from app.utils import get_sender_data, load_csv_data, get_best_sender_name, generate_message_with_openai_cot

app = FastAPI()

@app.post("/generate_message", response_model=MessageOutput)
async def generate_message_api(message_input: MessageInput):
    try:
        sender = message_input.sender
        generate_from_best = message_input.generate_from_best
        category = message_input.category

        df = load_csv_data()
        data = get_sender_data(df,sender, category)

        if data is None:
            if generate_from_best:
                # Randomly select a sender from the available data
                best_sender = get_best_sender_name(df)
                data = get_sender_data(df,best_sender, category)
            else:
                msg = (
                    f"Sender {sender} not found in the sample dataset. "
                    "Either use a sender name which already exists in the sample or "
                    "pass the argument `generate_from_best=true` to generate a message in the style of the best messages."
                    )
                raise HTTPException(status_code=404, detail=msg)
                

        new_message, reference_message = generate_message_with_openai_cot(data, message_input)
        return MessageOutput(
            message_body=new_message,
            reference_message=reference_message,
            status="Success"
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f'Error occurred while generating new message: {e}')
        raise HTTPException(status_code=500, detail="Error occurred while generating new message")