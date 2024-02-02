from fastapi import APIRouter

analytics_router = APIRouter(
    prefix="/analytics",
    tags=["email_analytics"],
)


@analytics_router.get("/")
async def email_analytics_root():
    return {"message": "Hello Email Analytics"}
