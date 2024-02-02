from fastapi import APIRouter

filtering_router = APIRouter(
    prefix="/filtering",
    tags=["email_filtering"],
)


@filtering_router.get("/")
async def email_filtering_root():
    return {"message": "Hello Email Filtering"}
