from fastapi import APIRouter

settings_router = APIRouter(
    prefix="/settings",
    tags=["email_settings"],
)


@settings_router.get("/")
async def email_settings_root():
    return {"message": "Hello Email Settings"}
