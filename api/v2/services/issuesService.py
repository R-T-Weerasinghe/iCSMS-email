from datetime import date
from typing import List, Optional
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
) ->IssuesResponse :
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
    return {
        "issues": [
            {
                "id": "1",
                "issue": "Issue 1",
                "isOverdue": False,
                "status": "New",
                "sender": "testSender@gmai.com",
                "recipient": "dfsfssf",
                "dateOpened": "2021-10-10T10:10:10",
                "tags": ["tag1", "tag2"],
            },
            {
                "id": "2",
                "issue": "Issue 2",
                "isOverdue": False,
                "status": "New",
                "sender": "dsffsf",
                "recipient": "sdgjnjsnj",
                "dateOpened": "2021-10-10T10:10:10",
                "tags": ["tag3", "tag4"],
            }
        ],
        "total": 2,
        "skip": skip,
        "limit": limit
    }