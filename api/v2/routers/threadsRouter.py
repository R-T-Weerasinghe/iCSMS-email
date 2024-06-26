from typing import List
from fastapi import APIRouter

from api.v2.models.threadsModel import ThreadSummaryResponse, AllThreadsSummaryResponse
from api.v2.services.threadsService import getHotThreads, getAllThreads

router = APIRouter()


@router.get("/threads/hot-threads", response_model=ThreadSummaryResponse)
async def get_hot_threads():
    return getHotThreads()


@router.get("/threads", response_model=AllThreadsSummaryResponse)
async def get_all_threads():
    return getAllThreads()



