from datetime import date, timedelta, datetime
from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException

from api.v2.dependencies.database import collection_issues, collection_configurations
from api.v2.models.issuesModel import IssueDetailed, Issue, IssueInDB
from api.v2.models.convoModel import EmailInDB
from api.v2.services.utilityService import (get_overdue_datetime, get_first_response_time, get_avg_response_time,
                                            get_resolution_time)

def getIssues(
    skip: int, 
    limit: int, 
    r: Optional[List[str]] = None,
    s: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    allTags: Optional[bool] = None,
    status: Optional[List[str]] = None,
    dateFrom: Optional[date] = None,
    dateTo: Optional[date] = None,
    q: Optional[str] = None,
    new: Optional[bool] = None,
    imp: Optional[bool] = None
):
    """
    Get issues based on the given parameters.
    """
    query = {}
    if skip is None:
        skip = 0
    if limit is None:
        limit = 10
    if r:
        query["recepient_email"] = {"$in": r}
    if s:
        query["sender_email"] = {"$in": s}
    if tags:
        if allTags:
            query["products"] = {"$all": tags}
        else:
            query["products"] = {"$in": tags}
    if status:
        query["status"] = {"$in": status}
        query["ongoing_status"] = {"$in": status}

    if dateFrom and dateTo:
        query["start_time"] = {"$gte": dateFrom, "$lte": dateTo}
    if q:
        query["$text"] = {"$search": q}
    # if new:
    #     query["status"] = "New"
    # if imp:
    #     query["tags"] = {"$in": ["important"]}
    issues = list(collection_issues.find(query).skip(skip).limit(limit))

    for i, issue in enumerate(issues):
        issue["id"] = str(issue["_id"])
        del issue["_id"]
        issues[i] = Issue.convert(IssueInDB(**issue))

    return {
        "issues": issues,
        "total": collection_issues.count_documents(query),
        "skip": skip,
        "limit": limit
    }


def getIssueByThreadId(thread_id: str) -> IssueDetailed:
    """
    Get an issue by its thread ID.
    """
    issue: dict = collection_issues.find_one({"thread_id": thread_id})
    if not issue:
        raise HTTPException(status_code=404, detail=f"Issue with the thread id {thread_id} not found")
    issue["id"] = str(issue["_id"])
    del issue["_id"]

    emails: List[EmailInDB] = issue["emails"]
    dateOverdue = get_overdue_datetime(issue["start_time"])
    firstResponseTime = get_first_response_time(emails)
    avgResponseTime = get_avg_response_time(emails)
    resolutionTime = get_resolution_time(emails, issue["status"])

    return IssueDetailed.convert_additional(
        IssueInDB(**issue), dateOverdue, firstResponseTime, avgResponseTime, resolutionTime
    )
