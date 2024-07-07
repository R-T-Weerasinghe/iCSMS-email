import datetime
from typing import List, Optional
from fastapi import APIRouter, Query, Depends
from .services import search_emails
from .models import Email, EmailRequest

router = APIRouter()

@router.get("/emails/search", response_model=List[Email])
async def search_email_route(params: EmailRequest = Depends()): # Depends to enforce params to be parameters instead of being request body
    return search_emails(**params.model_dump()) # pydantic model to python dict

# More secure since the parameters are not in the URL so that they are not saved in the browser history, logs etc.
@router.post("/emails/search", response_model=List[Email])
async def search_email_route(params: EmailRequest): 
    return search_emails(**params.model_dump()) # pydantic model to python dict

# @router.get("/emails/search", response_model=List[Email])
# async def search_emails_route(
#         subject: Optional[str] = Query(None),
#         sender: Optional[str] = Query(None),
#         receiver: Optional[str] = Query(None),
#         start_date: Optional[datetime.date] = Query(None),
#         end_date: Optional[datetime.date] = Query(None),
#         sentiment_lower: Optional[float] = Query(None),
#         sentiment_upper: Optional[float] = Query(None),
#         topics: Optional[List[str]] = Query(None),
#         limit: int = Query(10),
#         skip: int = Query(0)
# ):
#     return search_emails(
#         subject=subject,
#         sender=sender,
#         receiver=receiver, 
#         start_date=start_date, 
#         end_date=end_date, 
#         sentiment_lower=sentiment_lower, 
#         sentiment_upper=sentiment_upper,
#         topics=topics,
#         limit=limit,
#         skip=skip
#     )

# TODO: add a model to handle the params instead of writing them all out
# CHECKOUT: https://chat.openai.com/share/dd0445f9-3bed-441e-9fcb-63aac025aa84
