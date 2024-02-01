from fastapi import APIRouter

email_analytics_router = APIRouter(
    prefix="/analytics",
    tags=["email_analytics"],
)


@email_analytics_router.get("/")
async def email_analytics_root():
    return {"message": "Hello Email Analytics"}
