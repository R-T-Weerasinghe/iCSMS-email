import datetime
from typing import List, Optional
from fastapi import APIRouter, Query
from .services import get_all_conversations, search_conversations
from .models import ConversationOID, Conversation

router = APIRouter()


@router.get("/summaries/search", response_model=List[Conversation])
async def search_conversations_route(
        subject: Optional[str] = Query(None),
        sender: Optional[str] = Query(None),
        receiver: Optional[str] = Query(None),
        start_date: Optional[datetime.date] = Query(None),
        end_date: Optional[datetime.date] = Query(None),
        sentiment_lower: Optional[float] = Query(None),
        sentiment_upper: Optional[float] = Query(None),
        limit: int = Query(10),
        skip: int = Query(0)
):
    return search_conversations(
        subject=subject,
        sender=sender,
        receiver=receiver, 
        start_date=start_date, 
        end_date=end_date, 
        sentiment_lower=sentiment_lower, 
        sentiment_upper=sentiment_upper,
        limit=limit,
        skip=skip
    )


@router.get("/summaries/", response_model=List[ConversationOID])
async def get_conversations():
    return get_all_conversations()
