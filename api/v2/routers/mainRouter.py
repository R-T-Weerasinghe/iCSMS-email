from fastapi import APIRouter

from api.v2.routers.issuesRouter import router as issuesRouter
from api.v2.routers.inquiriesRouter import router as inquiriesRouter
from api.v2.routers.suggestionsRouter import router as suggestionsRouter
from api.v2.routers.filtersRouter import router as filterRouter
from api.v2.routers.dataRouter import router as dataRouter
from api.v2.routers.threadsRouter import router as threadsRouter
from api.v2.routers.dashboardRouter import router as dashboardRouter
from api.v2.routers.settingsRouter import router as settingsRouter
from api.v2.routers.BIAppsRouter import router as BIRouter

router = APIRouter()
router.include_router(issuesRouter)
router.include_router(inquiriesRouter)
router.include_router(suggestionsRouter)
router.include_router(filterRouter)
router.include_router(dataRouter)
router.include_router(threadsRouter)
router.include_router(dashboardRouter)
router.include_router(settingsRouter)
router.include_router(BIRouter)

@router.get("/")
async def root():
    return {"message": "Welcome to the Email Filtering API Version 2!"}
