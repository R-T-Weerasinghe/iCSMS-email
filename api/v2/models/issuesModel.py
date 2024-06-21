from typing import List, Literal, Optional
from fastapi import Query
from pydantic import BaseModel
from datetime import datetime


class EmailInDB(BaseModel):
    msgSummary: str
    person: Literal['Client', 'Company']
    dateTime: datetime


class IssueInDB(BaseModel):
    thread_id: str
    issue_summary: str
    convo_summary: Optional[List[EmailInDB]] = None
    status: Literal['new', 'waiting', 'update', 'closed']
    client: Optional[str] = None
    company: Optional[str] = None
    products: Optional[List[str]] = None
    isOverdue: Optional[bool] = None
    dateOpened: datetime
    dateClosed: Optional[datetime] = None
    dateUpdate: Optional[datetime] = None
    dateOverdue: Optional[datetime] = None
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
        return cls(
            id=issueInDB.thread_id,
            issue=issueInDB.issue_summary,
            status=issueInDB.status,
            client=issueInDB.client,
            company=issueInDB.company,
            tags=issueInDB.products,
            isOverdue=issueInDB.isOverdue,
            dateOpened=issueInDB.dateOpened,
            dateClosed=issueInDB.dateClosed,
            dateUpdate=issueInDB.dateUpdate,
            dateOverdue=issueInDB.dateOverdue,
            effectivity=issueInDB.effectivity,
            efficiency=issueInDB.efficiency,
        )


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
            body=emailInDB.msgSummary,
            isClient=emailInDB.person == "Client",
            dateTime=emailInDB.dateTime
        )


class IssueDetailed(Issue):
    dateOverdue: datetime
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
        return cls(
            id=issueInDB.thread_id,
            issue=issueInDB.issue_summary,
            status=issueInDB.status,
            client=issueInDB.client,
            company=issueInDB.company,
            tags=issueInDB.products,
            isOverdue=issueInDB.isOverdue,
            dateOpened=issueInDB.dateOpened,
            dateClosed=issueInDB.dateClosed,
            dateUpdate=issueInDB.dateUpdate,
            dateOverdue=issueInDB.dateOverdue,
            effectivity=issueInDB.effectivity,
            efficiency=issueInDB.efficiency,
            firstResponseTime=issueInDB.firstResponseTime,
            avgResponseTime=issueInDB.avgResponseTime,
            resolutionTime=issueInDB.resolutionTime,
            sentiment=issueInDB.sentiment,
            emails=[Email.convert(email) for email in issueInDB.convo_summary]
        )


class IssuesResponse(BaseModel):
    issues: List[Issue]
    total: int
    skip: int
    limit: int


