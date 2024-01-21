
# Pydantic allows auto creation of JSON Schemas from models
from pydantic import BaseModel

class Email(BaseModel):
    emailId: str
    receiverEmail: str
    senderEmail: str
    sentTime: str
    pulledTime: str
    maskedSubject: str
    maskedContent: str

