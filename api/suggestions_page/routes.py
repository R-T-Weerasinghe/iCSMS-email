from fastapi import APIRouter, HTTPException
from api.settings.models import IntergratingEmailData, NotiSendingChannelsRecord
from typing import Dict, Any
from api.email_filtering_and_info_generation.emailIntegration import integrateEmail
from api.email_filtering_and_info_generation.configurations.database import  collection_suggestions,collection_readingEmailAccounts, collection_configurations
from api.email_filtering_and_info_generation.routes import get_reading_emails_array
from api.settings.models import Trigger
from fastapi.responses import JSONResponse
import shutil



router = APIRouter()


# filtered suggestions listener
@router.get("/suggestion-filtering/get_filtered_suggestions?intervalIndays")
def get_filtered_suggestions(intervalIndays: int, productSelected: str, recipientEmailSelected: str):
    
    suggestions_docs = collection_suggestions.find({})


