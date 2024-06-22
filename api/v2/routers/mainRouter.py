from fastapi import APIRouter

from api.v2.routers.issuesRouter import router as issuesRouter
from api.v2.routers.inquiriesRouter import router as inquiriesRouter
from api.v2.routers.suggestionsRouter import router as suggestionsRouter
from api.v2.routers.filtersRouter import router as filterRouter

router = APIRouter()
router.include_router(issuesRouter)
router.include_router(inquiriesRouter)
router.include_router(suggestionsRouter)
router.include_router(filterRouter)


@router.get("/")
async def root():
    return {"message": "Welcome to the Email Filtering API Version 2!"}
