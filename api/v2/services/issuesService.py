from datetime import date
from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException

from api.v2.dependencies.database import collection_issues
from api.v2.models.issuesModel import IssuesResponse, Issue, IssueInDB


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
        query["company_address"] = {"$in": r}
    if s:
        query["client_address"] = {"$in": s}
    if tags:
        if allTags:
            query["tags"] = {"$all": tags}
        else:
            query["tags"] = {"$in": tags}
    if status:
        query["status"] = {"$in": status}
    if dateFrom and dateTo:
        query["dateOpened"] = {"$gte": dateFrom, "$lte": dateTo}
    # if q:
    #     query["$text"] = {"$search": q}
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


def getIssueById(issue_id: str) -> Issue:
    """
    Get an issue by its ID.
    """
    issue = collection_issues.find_one({"_id": ObjectId(issue_id)})
    if not issue:
        raise HTTPException(status_code=404, detail=f"Issue with the id {issue_id} not found")
    issue["id"] = str(issue["_id"])
    del issue["_id"]
    return Issue.convert(IssueInDB(**issue))


def getIssueByThreadId(thread_id: str) -> Issue:
    """
    Get an issue by its thread ID.
    """
    issue = collection_issues.find_one({"thread_id": thread_id})
    if not issue:
        raise HTTPException(status_code=404, detail=f"Issue with the thread id {thread_id} not found")
    issue["id"] = str(issue["_id"])
    del issue["_id"]
    return Issue.convert(IssueInDB(**issue))