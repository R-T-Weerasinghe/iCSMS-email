from fastapi import APIRouter

email_filtering_router = APIRouter(
    prefix="/filtering",
    tags=["email_filtering"],
)


@email_filtering_router.get("/")
async def email_filtering_root():
    return {"message": "Hello Email Filtering"}
