import datetime
from typing import List, Optional
from pydantic import BaseModel

class ThreadSummary(BaseModel):
    subject: str
    snippet: str
    summary: str
    lastUpdate: datetime
    tags: List[str]
    
class ThreadSummaryResponse(BaseModel):
    threads: List[ThreadSummary]
    total:int
       
class GeneralThreadSummary(BaseModel):
    subject: str
    type: str
    snippet: str
    summary: str
    lastUpdate: datetime
    tags: List[str]

class AllThreadsSummaryResponse(BaseModel):
    threads: List[GeneralThreadSummary]
    total:int