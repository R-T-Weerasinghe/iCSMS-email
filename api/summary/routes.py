from typing import List
from fastapi import APIRouter
from .services import get_all_conversations
from .models import Conversation

router = APIRouter()


@router.get("/summaries/", response_model=List[Conversation])
async def get_conversations():
    return get_all_conversations()