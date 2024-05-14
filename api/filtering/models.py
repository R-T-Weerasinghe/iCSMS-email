# Validation, response and other models
from typing import List, Optional
from pydantic import BaseModel
from fastapi import Query
from datetime import datetime, date


class EmailOID(BaseModel):
    id: str
    thread_id: str
    subject: Optional[str]
    sentiment: str
    sender: str
    receiver: str
    topics: Optional[list]


class Email(BaseModel):
    id: str
    subject: Optional[str]
    sender: str
    receiver: str
    datetime: datetime
    our_sentiment_score: float
    topics: Optional[list]


class EmailRequest(BaseModel):
    subject: Optional[str] = None
    sender: Optional[str] = None
    receiver: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    sentiment_lower: Optional[float] = None
    sentiment_upper: Optional[float] = None
    topics: Optional[List[str]] = None
    limit: int = 10
    skip: int = 0
