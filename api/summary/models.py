# Validation, response and other models
from typing import Optional
from pydantic import BaseModel

class Conversation(BaseModel):
    id: str
    thread_id: str
    subject: Optional[str]
    sentiment: str
    sender: str
    receiver: str
    summary: str


        

