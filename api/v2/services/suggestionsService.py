from datetime import date
from typing import List, Optional
from fastapi import HTTPException

from api.v2.dependencies.database import collection_suggestions
from api.v2.models.suggestionsModel import Suggestion, SuggestionInDB
from api.v2.services.utilityService import build_query


def getSuggestions(
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
    Get suggestions based on the given parameters.
    """
    query = build_query(skip, limit, "suggestion", r, s, tags, allTags, status, dateFrom, dateTo, q)
    suggestions = list(collection_suggestions.find(query).skip(skip).limit(limit))

    for i, suggestion in enumerate(suggestions):
        suggestion["id"] = str(suggestion["_id"])
        del suggestion["_id"]
        suggestions[i] = Suggestion.convert(SuggestionInDB(**suggestion))

    return {
        "suggestions": suggestions,
        "total": collection_suggestions.count_documents(query),
        "skip": skip,
        "limit": limit
    }


def getSuggestionByThreadId(thread_id: str) -> Suggestion:
    """
    Get an issue by its thread ID.
    """
    issue = collection_suggestions.find_one({"thread_id": thread_id})
    if not issue:
        raise HTTPException(status_code=404, detail=f"Suggestion with the thread id {thread_id} not found")
    issue["id"] = str(issue["_id"])
    del issue["_id"]
    return Suggestion.convert(SuggestionInDB(**issue))