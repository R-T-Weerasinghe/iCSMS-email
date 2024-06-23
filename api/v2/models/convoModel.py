from pydantic import BaseModel
from typing import List, Literal, Optional
from datetime import datetime


class EmailInDB(BaseModel):
    message: str
    sender_type: Literal['Client', 'Company']
    time: datetime


class Email(BaseModel):
    body: str
    isClient: bool
    dateTime: datetime

    @classmethod
    def convert(cls, emailInDB: EmailInDB) -> 'Email':
        """
        Converts an EmailInDB object to an Email object.
        """
        return cls(
            body=emailInDB.message,
            isClient=emailInDB.sender_type == "Client",
            dateTime=emailInDB.time
        )
