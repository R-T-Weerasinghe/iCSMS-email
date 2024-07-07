from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ThreadInDB(BaseModel):
    thread_id: str
    subject: str
    summary: str
    updated_times: List[datetime]
    products: List[str]


class ThreadSummary(BaseModel):
    subject: str
    snippet: str
    summary: str
    lastUpdate: datetime
    tags: List[str]


class ThreadSummaryResponse(BaseModel):
    threads: List[ThreadSummary]
    total: int
    limit: int = 10
    skip: int = 0


class GeneralThreadSummary(BaseModel):
    subject: str
    type: str
    snippet: str
    summary: str
    lastUpdate: datetime
    tags: List[str]


class AllThreadsSummaryResponse(BaseModel):
    threads: List[GeneralThreadSummary]
    total: int
    limit: int = 10
    skip: int = 0


class ConvoSummaryResponse(BaseModel):
    summary: str

    @classmethod
    def convert(cls, thread: ThreadInDB) -> "ConvoSummaryResponse":
        return cls(
            summary=thread.summary
        )