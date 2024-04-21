# Validation, response and other models
from typing import Optional
from pydantic import BaseModel

class ConversationOID(BaseModel):
    id: str
    thread_id: str
    subject: Optional[str]
    sentiment: str
    sender: str
    receiver: str
    summary: str

class Conversation(BaseModel):
    thread_id: str
    subject: Optional[str]
    sentiment: str
    sender: str
    receiver: str
    summary: str
        

