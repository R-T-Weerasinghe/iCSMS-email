import asyncio
import uvicorn  # debugging
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from api.email_filtering_and_info_generation.check_notifications import check_notifications_for_managers
from api.email_filtering_and_info_generation.read_emails import repeat_every_10mins
from utils.sliding_window_deletion import slide_the_time_window

from api.summary.routes import router as conversation_router
from api.email_authorization.routes import router as authorization_router
from api.filtering.routes import router as filtering_router
from api.settings.routes import router as settings_router
from api.dashboard.routes import router as dashboard_router
from api.v2.routers.dashboardRouter import router as dashboard_router_v2
from api.v2.routers.settingsRouter import router as settings_router_v2
from api.suggestions_page.routes import router as suggestions_router
from api.v2.routers.mainRouter import router as v2_router

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

EMAIL_PREFIX = "/email"

app.include_router(conversation_router, prefix=EMAIL_PREFIX)
app.include_router(settings_router, prefix=EMAIL_PREFIX)
app.include_router(filtering_router, prefix=EMAIL_PREFIX)
app.include_router(authorization_router, prefix=EMAIL_PREFIX)
app.include_router(dashboard_router,prefix=EMAIL_PREFIX)
app.include_router(suggestions_router,prefix=EMAIL_PREFIX)
app.include_router(v2_router, prefix=f"{EMAIL_PREFIX}/v2")



def retrieving_emails_loop():
    asyncio.run(repeat_every_10mins())


def check_notifications_loop():
    print("in main.py check_notifications_loop")
    asyncio.run(check_notifications_for_managers())


def slide_time_window_loop():
    try:
        asyncio.run(slide_the_time_window())
    except Exception as e:
        print(f"An error occurred: {e}")


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url='/docs')

if __name__ == "__main__":
    uvicorn.run(app)