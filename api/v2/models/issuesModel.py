from typing import List, Literal, Optional
from fastapi import Query
from pydantic import BaseModel
from datetime import datetime

from .convoModel import EmailInDB, Email


class IssueInDB(BaseModel):
    thread_id: str
    thread_subject: str
    recepient_email: str
    sender_email: str
    issue_summary: str
    issue_convo_summary_arr: Optional[List[EmailInDB]] = None
    status: Literal['ongoing', 'closed']
    ongoing_status: Optional[Literal['new', 'waiting', 'update']]
    issue_type: Optional[str] = None
    products: Optional[List[str]] = None
    sentiment_score: Optional[float] = None
    start_time: datetime
    updated_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    effectivity: Optional[int] = None
    efficiency: Optional[int] = None
    isOverdue: Optional[bool] = None


class Issue(BaseModel):
    id: str
    issue: str
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
    def convert(cls, issueInDB: IssueInDB) -> 'Issue':
        """
        Converts an IssueInDB object to an Issue object.
        """
        if issueInDB.status == "ongoing":
            status = issueInDB.ongoing_status
        else:
            status = issueInDB.status
        return cls(
            id=issueInDB.thread_id,
            issue=issueInDB.issue_summary,
            subject=issueInDB.thread_subject,
            status=status,
            client=issueInDB.sender_email,
            company=issueInDB.recepient_email,
            tags=issueInDB.products,
            isOverdue=issueInDB.isOverdue,
            dateOpened=issueInDB.start_time,
            dateClosed=issueInDB.end_time,
            dateUpdate=issueInDB.updated_time,
            effectivity=issueInDB.effectivity,
            efficiency=issueInDB.efficiency,
        )


class IssueDetailed(Issue):
    dateOverdue: datetime
    emails: List[Email]
    # for a not replied email, these can be none
    firstResponseTime: Optional[int] = None  # in minutes
    avgResponseTime: Optional[int] = None  # in minutes
    resolutionTime: Optional[int] = None  # in minutes
    sentiment: Optional[float] = None

    @classmethod
    def convert_additional(
            cls, issueInDB: IssueInDB,
            dateOverdue: datetime,
            firstResponseTime: int | None,
            avgResponseTime: int | None,
            resolutionTime: int | None
    ) -> 'IssueDetailed':
        """
        Converts an IssueInDB object to an IssueDetailed object.
        """
        if issueInDB.status == "ongoing":
            status = issueInDB.ongoing_status
        else:
            status = issueInDB.status
        return cls(
            id=issueInDB.thread_id,
            issue=issueInDB.issue_summary,
            subject=issueInDB.thread_subject,
            status=status,
            client=issueInDB.sender_email,
            company=issueInDB.recepient_email,
            tags=issueInDB.products,
            isOverdue=issueInDB.isOverdue,
            dateOpened=issueInDB.start_time,
            dateClosed=issueInDB.end_time,
            dateUpdate=issueInDB.updated_time,
            dateOverdue=dateOverdue,
            effectivity=issueInDB.effectivity,
            efficiency=issueInDB.efficiency,
            firstResponseTime=firstResponseTime,
            avgResponseTime=avgResponseTime,
            resolutionTime=resolutionTime,
            sentiment=issueInDB.sentiment_score,
            emails=[Email.convert(email) for email in issueInDB.issue_convo_summary_arr]
        )


class IssuesResponse(BaseModel):
    issues: List[Issue]
    total: int
    skip: int
    limit: int
