from typing import List, Literal, Optional
from pydantic import BaseModel
from datetime import datetime

from .convoModel import EmailInDB, Email

class SuggestionInDB(BaseModel):
    thread_id: str
    suggestion_summary: str
    suggestion_convo_summary_arr: Optional[List[EmailInDB]] = None
    status: Literal['ongoing', 'closed']
    ongoing_status: Optional[Literal['new', 'waiting', 'update']]
    recepient_email: str
    sender_email: str
    suggestion_type: Optional[str] = None
    products: Optional[List[str]] = None
    isOverdue: Optional[bool] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    effectivity: Optional[int] = None
    efficiency: Optional[int] = None
    firstResponseTime: Optional[int] = None  # in minutes
    avgResponseTime: Optional[int] = None    # in minutes
    resolutionTime: Optional[int] = None     # in minutes
    sentiment: Optional[str] = None


class Suggestion(BaseModel):
    id: str
    suggestion: str
    status: Literal['new', 'waiting', 'update', 'closed']
    client: str
    company: str
    tags: List[str]
    dateOpened: datetime
    dateClosed: Optional[datetime] = None
    dateUpdate: Optional[datetime] = None
    isOverdue: Optional[bool] = None
    effectivity: Optional[int] = None
    efficiency: Optional[int] = None

    @classmethod
    def convert(cls, suggestionInDB: SuggestionInDB) -> 'Suggestion':
        """
        Converts an SuggestionInDB object to an Suggestion object.
        """
        if suggestionInDB.status == "ongoing":
            status = suggestionInDB.ongoing_status
        else:
            status = suggestionInDB.status
        return cls(
            id=suggestionInDB.thread_id,
            suggestion=suggestionInDB.suggestion_summary,
            status=status,
            client=suggestionInDB.sender_email,
            company=suggestionInDB.recepient_email,
            tags=suggestionInDB.products,
            isOverdue=suggestionInDB.isOverdue,
            dateOpened=suggestionInDB.start_time,
            dateClosed=suggestionInDB.end_time,
            dateUpdate=suggestionInDB.updated_time,
            dateOverdue=None,
            effectivity=suggestionInDB.effectivity,
            efficiency=suggestionInDB.efficiency,
        )


class SuggestionDetailed(Suggestion):
    dateOverdue: Optional[datetime] = None
    firstResponseTime: Optional[int] = None # in minutes
    avgResponseTime: Optional[int] = None   # in minutes
    resolutionTime: Optional[int] = None    # in minutes
    sentiment: Optional[str] = None
    emails: List[Email]

    @classmethod
    def convert(cls, suggestionInDB: SuggestionInDB) -> 'SuggestionDetailed':
        """
        Converts an SuggestionInDB object to an SuggestionDetailed object.
        """
        if suggestionInDB.status == "ongoing":
            status = suggestionInDB.ongoing_status
        else:
            status = suggestionInDB.status
        return cls(
            id=suggestionInDB.thread_id,
            suggestion=suggestionInDB.suggestion_summary,
            status=status,
            client=suggestionInDB.sender_email,
            company=suggestionInDB.recepient_email,
            tags=suggestionInDB.products,
            isOverdue=suggestionInDB.isOverdue,
            dateOpened=suggestionInDB.start_time,
            dateClosed=suggestionInDB.end_time,
            dateUpdate=suggestionInDB.updated_time,
            dateOverdue=suggestionInDB.dateOverdue,
            effectivity=suggestionInDB.effectivity,
            efficiency=suggestionInDB.efficiency,
            firstResponseTime=suggestionInDB.firstResponseTime,
            avgResponseTime=suggestionInDB.avgResponseTime,
            resolutionTime=suggestionInDB.resolutionTime,
            sentiment=suggestionInDB.sentiment,
            emails=[Email.convert(email) for email in suggestionInDB.suggestion_convo_summary_arr]
        )


class SuggestionsResponse(BaseModel):
    suggestions: List[Suggestion]
    total: int
    skip: int
    limit: int


