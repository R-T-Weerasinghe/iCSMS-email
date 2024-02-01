from fastapi import APIRouter

email_summaries_router = APIRouter(
    prefix="/summaries",
    tags=["email_summaries"],
)


@email_summaries_router.get("/")
async def email_summaries_root():
    return {"message": "Hello Email Summaries"}
