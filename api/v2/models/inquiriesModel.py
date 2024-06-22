from typing import List, Literal, Optional
from fastapi import Query
from pydantic import BaseModel
from datetime import datetime

from .convoModel import EmailInDB, Email


class InquiryInDB(BaseModel):
    thread_id: str
    inquiry_summary: str
    inquiry_convo_summary_arr: Optional[List[EmailInDB]] = None
    status: Literal['ongoing', 'closed']
    ongoing_status: Optional[Literal['new', 'waiting', 'update']]
    recepient_email: str
    sender_email: str
    inquiry_type: Optional[str] = None
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


class Inquiry(BaseModel):
    id: str
    inquiry: str
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
            status=status,
            client=inquiryInDB.sender_email,
            company=inquiryInDB.recepient_email,
            tags=inquiryInDB.products,
            isOverdue=inquiryInDB.isOverdue,
            dateOpened=inquiryInDB.start_time,
            dateClosed=inquiryInDB.end_time,
            dateUpdate=inquiryInDB.updated_time,
            dateOverdue=None,
            effectivity=inquiryInDB.effectivity,
            efficiency=inquiryInDB.efficiency,
        )


class InquiryDetailed(Inquiry):
    dateOverdue: Optional[datetime] = None
    firstResponseTime: Optional[int] = None # in minutes
    avgResponseTime: Optional[int] = None   # in minutes
    resolutionTime: Optional[int] = None    # in minutes
    sentiment: Optional[str] = None
    emails: List[Email]

    @classmethod
    def convert(cls, inquiryInDB: InquiryInDB) -> 'InquiryDetailed':
        """
        Converts an InquiryInDB object to an InquiryDetailed object.
        """
        if inquiryInDB.status == "ongoing":
            status = inquiryInDB.ongoing_status
        else:
            status = inquiryInDB.status
        return cls(
            id=inquiryInDB.thread_id,
            inquiry=inquiryInDB.inquiry_summary,
            status=status,
            client=inquiryInDB.sender_email,
            company=inquiryInDB.recepient_email,
            tags=inquiryInDB.products,
            isOverdue=inquiryInDB.isOverdue,
            dateOpened=inquiryInDB.start_time,
            dateClosed=inquiryInDB.end_time,
            dateUpdate=inquiryInDB.updated_time,
            dateOverdue=inquiryInDB.dateOverdue,
            effectivity=inquiryInDB.effectivity,
            efficiency=inquiryInDB.efficiency,
            firstResponseTime=inquiryInDB.firstResponseTime,
            avgResponseTime=inquiryInDB.avgResponseTime,
            resolutionTime=inquiryInDB.resolutionTime,
            sentiment=inquiryInDB.sentiment,
            emails=[Email.convert(email) for email in inquiryInDB.inquiry_convo_summary_arr]
        )


class InquiriesResponse(BaseModel):
    inquiries: List[Inquiry]
    total: int
    skip: int
    limit: int


