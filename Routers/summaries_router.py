from fastapi import APIRouter

summaries_router = APIRouter(
    prefix="/summaries",
    tags=["email_summaries"],
)


@summaries_router.get("/")
async def email_summaries_root():
    return {"message": "Hello Email Summaries"}
