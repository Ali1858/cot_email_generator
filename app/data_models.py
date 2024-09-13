from pydantic import BaseModel
from typing import Optional

class MessageInput(BaseModel):
    "Data model for Input Request"
    sender: str
    receiver: str
    category: str
    signal: str
    generate_from_best: Optional[bool] = False

class MessageOutput(BaseModel):
    "Data model for Output Request"
    message_body: str
    reference_message: Optional[str] = None
    status: str