from typing import TypedDict

class Email(TypedDict):
    subject: str
    senderEmail: str
    receiverEmail: str
    sentTime: str
    emailId: str
    body: str
    pulledTime: str

