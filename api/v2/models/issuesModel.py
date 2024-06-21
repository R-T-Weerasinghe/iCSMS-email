from typing import List, Literal, Optional
from fastapi import Query
from pydantic import BaseModel, Field, SerializeAsAny, field_validator
from datetime import datetime, date
from .utilsModel import parse_to_list

class IssueInDB(BaseModel):
    thread_id: str
    issue_convo_summary: str
    status: Optional[str] = None
    sender: Optional[str] = None
    recipient: Optional[str] = None
    tags: Optional[List[str]] = None
    isOverdue: Optional[bool] = None
    start_time: datetime
    dateClosed: Optional[datetime] = None
    dateUpdate: Optional[datetime] = None
    effectivity: Optional[int] = None
    efficiency: Optional[int] = None

class Issue(BaseModel):
    id: str
    issue: str
    # status: Literal['New', 'Waiting', 'Update', 'Closed']
    status: str # NOTE: only for testing purposes
    sender: str
    recipient: str
    tags: List[str]
    dateOpened: datetime
    isOverdue: Optional[bool] = None
    dateClosed: Optional[datetime] = None
    dateUpdate: Optional[datetime] = None
    effectivity: Optional[int] = None
    efficiency: Optional[int] = None

    @classmethod
    def convert(cls, issueInDB: IssueInDB) -> 'Issue':
        """
        Converts an IssueInDB object to an Issue object.

        Args:
            issueInDB: The IssueInDB object to be converted.

        Returns:
            Issue: The converted Issue object.
        """
        return cls(
            id=issueInDB.thread_id,
            issue=issueInDB.issue_convo_summary,
            status="New",
            sender="testSender@gmail.com",
            recipient="testSender@gmail.com",
            tags=["tag1", "tag2"],
            dateOpened=issueInDB.start_time
            # status=issueInDB.status,
            # sender=issueInDB.sender,
            # recipient=issueInDB.recipient,
            # tags=issueInDB.tags,
            # isOverdue=issueInDB.isOverdue,
            # dateOpened=issueInDB.dateOpened,
            # dateClosed=issueInDB.dateClosed,
            # dateUpdate=issueInDB.dateUpdate,
            # effectivity=issueInDB.effectivity,
            # efficiency=issueInDB.efficiency
        )


class IssuesResponse(BaseModel):
    issues: List[Issue]
    total: int
    skip: int
    limit: int
    
class IssuesParams(BaseModel):
    # NOTE: SerializeAsAny is used to suppress a *warning* given by Pydantic when handling arrays. This is a bug in Pydantic.
    # NOTE: Moreinfo: https://github.com/pydantic/pydantic/issues/7905
    r: Optional[SerializeAsAny[str]] = Field(
        Query(None, description="Recipient email addresses"))
    s: Optional[SerializeAsAny[str]] = Field(
        Query(None, description="Sender email addresses"))
    tags: Optional[SerializeAsAny[str]] = Field(
        Query(None, description="Tags associated with the issue"))
    allTags: Optional[bool] = Field(
        Query(None, description="Indicates if all tags should be present"))
    status: Optional[SerializeAsAny[str]] = Field(
        Query(None, description="Status of the issue"))
    # date: Optional[str] = Field(Query(None, description="Dates in between which the issue was opened"))
    dateFrom: Optional[date] = Field(
        Query(None, description="Start date for the issue (inclusive)"))
    dateTo: Optional[date] = Field(
        Query(None, description="End date for the issue (inclusive)"))
    q: Optional[str] = Field(Query(None, description="Search query"))
    new: Optional[bool] = Field(
        Query(None, description="Indicates if the issue is new"))
    imp: Optional[bool] = Field(
        Query(None, description="Indicates if the issue is important"))
    skip: int = Field(
        Query(None, description="Number of records to skip"))
    limit: int = Field(
        Query(None, description="Number of records to return"))

    _to_list = field_validator('r', 's', 'tags', 'status')(parse_to_list)
