from typing import List, Literal, Optional
from pydantic import BaseModel
from datetime import datetime

from .convoModel import EmailInDB, Email


class InquiryInDB(BaseModel):
    thread_id: str
    thread_subject: str
    recepient_email: str
    sender_email: str
    inquiry_summary: str
    inquiry_convo_summary_arr: Optional[List[EmailInDB]] = None
    status: Literal['ongoing', 'closed']
    ongoing_status: Optional[Literal['new', 'waiting', 'update']]
    inquiry_type: Optional[str] = None
    products: Optional[List[str]] = None
    sentiment_score: Optional[float] = None
    start_time: datetime
    updated_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    effectiveness: Optional[int] = None
    efficiency: Optional[int] = None
    isOverdue: Optional[bool] = None


class Inquiry(BaseModel):
    id: str
    inquiry: str
    subject: str
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
    def convert(cls, inquiryInDB: InquiryInDB) -> 'Inquiry':
        """
        Converts an InquiryInDB object to an Inquiry object.
        """
        if inquiryInDB.status == "ongoing":
            status = inquiryInDB.ongoing_status
        else:
            status = inquiryInDB.status
        return cls(
            id=inquiryInDB.thread_id,
            inquiry=inquiryInDB.inquiry_summary,
            subject=inquiryInDB.thread_subject,
            status=status,
            client=inquiryInDB.sender_email,
            company=inquiryInDB.recepient_email,
            tags=inquiryInDB.products,
            isOverdue=inquiryInDB.isOverdue,
            dateOpened=inquiryInDB.start_time,
            dateClosed=inquiryInDB.end_time,
            dateUpdate=inquiryInDB.updated_time,
            effectivity=inquiryInDB.effectiveness,
            efficiency=inquiryInDB.efficiency,
        )


class InquiryDetailed(Inquiry):
    dateOverdue: datetime
    emails: List[Email]
    # for a not replied email, these can be none
    firstResponseTime: int | None = None  # in minutes
    avgResponseTime: int | None = None  # in minutes
    resolutionTime: int | None = None  # in minutes
    sentiment: float = None

    @classmethod
    def convert_additional(
        cls, inquiryInDB: InquiryInDB,
        dateOverdue: datetime,
        firstResponseTime: int | None,
        avgResponseTime: int | None,
        resolutionTime: int | None
    ) -> 'InquiryDetailed':
        """
        Converts an IssueInDB object to an IssueDetailed object.
        """
        if inquiryInDB.status == "ongoing":
            status = inquiryInDB.ongoing_status
        else:
            status = inquiryInDB.status
        return cls(
            id=inquiryInDB.thread_id,
            inquiry=inquiryInDB.inquiry_summary,
            subject=inquiryInDB.thread_subject,
            status=status,
            client=inquiryInDB.sender_email,
            company=inquiryInDB.recepient_email,
            tags=inquiryInDB.products,
            isOverdue=inquiryInDB.isOverdue,
            dateOpened=inquiryInDB.start_time,
            dateClosed=inquiryInDB.end_time,
            dateUpdate=inquiryInDB.updated_time,
            dateOverdue=dateOverdue,
            effectivity=inquiryInDB.effectiveness,
            efficiency=inquiryInDB.efficiency,
            firstResponseTime=firstResponseTime,
            avgResponseTime=avgResponseTime,
            resolutionTime=resolutionTime,
            sentiment=inquiryInDB.sentiment_score,
            emails=[Email.convert(email) for email in inquiryInDB.inquiry_convo_summary_arr]
        )


class InquiriesResponse(BaseModel):
    inquiries: List[Inquiry]
    total: int
    skip: int
    limit: int


