from typing import List
from fastapi import APIRouter, Query



from api.thread_summaries_page.models import ThreadSummaryResponse, AllThreadsSummaryResponse
from api.thread_summaries_page import services 
router = APIRouter()


@router.get("/thread_summaries/getHotThreads", response_model=List[ThreadSummaryResponse])
async def getHotThreads():
    

    result: ThreadSummaryResponse = services.getHotThreads()
    return result

@router.get("/thread_summaries/getAllThreads", response_model=List[AllThreadsSummaryResponse])
async def getAllThreads():
    

    result: AllThreadsSummaryResponse = services.getALLThreads()
    return result
    
        
    
    