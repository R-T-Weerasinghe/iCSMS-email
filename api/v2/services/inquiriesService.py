from datetime import date
from typing import List, Optional
from fastapi import HTTPException

from api.v2.dependencies.database import collection_inquiries
from api.v2.models.inquiriesModel import InquiriesResponse, Inquiry, InquiryInDB


def getInquiries(
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
    Get inquiries based on the given parameters.
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
    # if q:
    #     query["$text"] = {"$search": q}
    # if new:
    #     query["status"] = "New"
    # if imp:
    #     query["tags"] = {"$in": ["important"]}
    inquiries = list(collection_inquiries.find(query).skip(skip).limit(limit))

    for i, inquiry in enumerate(inquiries):
        inquiry["id"] = str(inquiry["_id"])
        del inquiry["_id"]
        inquiries[i] = Inquiry.convert(InquiryInDB(**inquiry))

    return {
        "inquiries": inquiries,
        "total": collection_inquiries.count_documents(query),
        "skip": skip,
        "limit": limit
    }


def getInquiryByThreadId(thread_id: str) -> Inquiry:
    """
    Get an issue by its thread ID.
    """
    issue = collection_inquiries.find_one({"thread_id": thread_id})
    if not issue:
        raise HTTPException(status_code=404, detail=f"Inquiry with the thread id {thread_id} not found")
    issue["id"] = str(issue["_id"])
    del issue["_id"]
    return Inquiry.convert(InquiryInDB(**issue))