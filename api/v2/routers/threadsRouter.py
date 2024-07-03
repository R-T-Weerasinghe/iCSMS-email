from typing import List
from fastapi import APIRouter

from api.v2.models.threadsModel import ThreadSummaryResponse, AllThreadsSummaryResponse, ConvoSummaryResponse
from api.v2.services.threadsService import getHotThreads, getAllThreads, getThreadSummary

router = APIRouter()


@router.get("/threads/hot-threads", response_model=ThreadSummaryResponse)
async def get_hot_threads():
    return await getHotThreads()

@router.get("/threads/summary/{thread_id}", response_model=ConvoSummaryResponse)
def get_thread_summary(thread_id: str):
    return getThreadSummary(thread_id)

@router.get("/threads", response_model=AllThreadsSummaryResponse)
async def get_all_threads():
    return await getAllThreads()



