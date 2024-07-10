from datetime import date
from typing import List, Optional
from fastapi import HTTPException
from pydantic import ValidationError

from api.v2.dependencies.database import collection_inquiries
from api.v2.models.convoModel import EmailInDB
from api.v2.models.inquiriesModel import InquiryDetailed, Inquiry, InquiryInDB
from api.v2.services.utilityService import get_overdue_datetime, get_first_response_time, get_avg_response_time, \
    get_resolution_time, build_query


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
    query = build_query(skip, limit, "inquiry", r, s, tags, allTags, status, dateFrom, dateTo, q)
    inquiries: List[dict] = list(
        collection_inquiries
            .find(query)
            .sort([('start_time', -1), ('updated_time', -1)])
            .skip(skip)
            .limit(limit)
    )
    try:
        inquiries_objs = [InquiryInDB(**inquiry) for inquiry in inquiries]
    except ValidationError:
        raise HTTPException(status_code=500, detail="Database schema error. Schema mismatch")
    inquiries_return: List[Inquiry] = [Inquiry.convert(inquiry) for inquiry in inquiries_objs]

    return {
        "inquiries": inquiries_return,
        "total": collection_inquiries.count_documents(query),
        "skip": skip,
        "limit": limit
    }


def getInquiryByThreadId(thread_id: str) -> Inquiry:
    """
    Get an issue by its thread ID.
    """
    inquiry: dict = collection_inquiries.find_one({"thread_id": thread_id})
    if not inquiry:
        raise HTTPException(status_code=404, detail=f"Inquiry with the thread id {thread_id} not found")
    try:
        inquiry_obj = InquiryInDB(**inquiry)
    except ValidationError:
        raise HTTPException(status_code=500, detail="Database schema error. Schema mismatch")
    emails: List[EmailInDB] = inquiry_obj.inquiry_convo_summary_arr
    dateOverdue = get_overdue_datetime(inquiry_obj.start_time)
    firstResponseTime = get_first_response_time(emails)
    avgResponseTime = get_avg_response_time(emails)
    resolutionTime = get_resolution_time(emails, inquiry_obj.status)

    return InquiryDetailed.convert_additional(
        InquiryInDB(**inquiry), dateOverdue, firstResponseTime, avgResponseTime, resolutionTime
    )