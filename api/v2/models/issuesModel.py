from typing import List, Literal, Optional
from fastapi import Query
from pydantic import BaseModel
from datetime import datetime

from .convoModel import EmailInDB, Email

class IssueInDB(BaseModel):
    thread_id: str
    issue_summary: str
    issue_convo_summary_arr: Optional[List[EmailInDB]] = None
    status: Literal['ongoing', 'closed']
    ongoing_status: Optional[Literal['new', 'waiting', 'update']]
    recepient_email: str
    sender_email: str
    issue_type: Optional[str] = None
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


class Issue(BaseModel):
    id: str
    issue: str
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
            status=status,
            client=issueInDB.sender_email,
            company=issueInDB.recepient_email,
            tags=issueInDB.products,
            isOverdue=issueInDB.isOverdue,
            dateOpened=issueInDB.start_time,
            dateClosed=issueInDB.end_time,
            dateUpdate=issueInDB.updated_time,
            dateOverdue=None,
            effectivity=issueInDB.effectivity,
            efficiency=issueInDB.efficiency,
        )


class IssueDetailed(Issue):
    dateOverdue: Optional[datetime] = None
    firstResponseTime: Optional[int] = None # in minutes
    avgResponseTime: Optional[int] = None   # in minutes
    resolutionTime: Optional[int] = None    # in minutes
    sentiment: Optional[str] = None
    emails: List[Email]

    @classmethod
    def convert(cls, issueInDB: IssueInDB) -> 'IssueDetailed':
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
            status=status,
            client=issueInDB.sender_email,
            company=issueInDB.recepient_email,
            tags=issueInDB.products,
            isOverdue=issueInDB.isOverdue,
            dateOpened=issueInDB.start_time,
            dateClosed=issueInDB.end_time,
            dateUpdate=issueInDB.updated_time,
            dateOverdue=issueInDB.dateOverdue,
            effectivity=issueInDB.effectivity,
            efficiency=issueInDB.efficiency,
            firstResponseTime=issueInDB.firstResponseTime,
            avgResponseTime=issueInDB.avgResponseTime,
            resolutionTime=issueInDB.resolutionTime,
            sentiment=issueInDB.sentiment,
            emails=[Email.convert(email) for email in issueInDB.issue_convo_summary_arr]
        )


class IssuesResponse(BaseModel):
    issues: List[Issue]
    total: int
    skip: int
    limit: int


