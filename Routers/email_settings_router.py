from fastapi import APIRouter

email_settings_router = APIRouter(
    prefix="/settings",
    tags=["email_settings"],
)


@email_settings_router.get("/")
async def email_settings_root():
    return {"message": "Hello Email Settings"}
