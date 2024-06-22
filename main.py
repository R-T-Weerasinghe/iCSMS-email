# main file that app starts with

# This has to be outside because of the way the app is structured
# Otherwise the relative imports within api/ and other modules won't work
# This is because the app is started from the root directory and python path is set to the root directory
# so all the imports can be called relative to the root directory
import asyncio
import threading
import time
from pydantic import ValidationError
import uvicorn  # debugging
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from api.summary.routes import router as conversation_router

from api.email_filtering_and_info_generation.routes import router as retrieval_and_info_router
from api.filtering.routes import router as filtering_router
from api.settings.routes import router as settings_router
from api.dashboard.routes import router as dashboard_router
from api.suggestions_page.routes import router as suggestions_router
from api.email_filtering_and_info_generation.read_emails import repeat_every_10mins
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from api.v2.routers.mainRouter import router as v2_router

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

EMAIL_PREFIX = "/email"

app.include_router(conversation_router, prefix=EMAIL_PREFIX)
app.include_router(settings_router, prefix=EMAIL_PREFIX)
app.include_router(filtering_router, prefix=EMAIL_PREFIX)
app.include_router(retrieval_and_info_router, prefix=EMAIL_PREFIX)
app.include_router(dashboard_router, prefix=EMAIL_PREFIX)
app.include_router(suggestions_router, prefix=EMAIL_PREFIX)
app.include_router(v2_router, prefix=f"{EMAIL_PREFIX}/v2")


def run_in_thread():
    asyncio.run(repeat_every_10mins())


def check_notifications_loop():
    pass


# @app.on_event("startup")
# async def on_startup():

#     # start the continous loop to extract emails in a new thread
#     threading.Thread(target=run_in_thread, args=(), daemon=True).start()

#     # start the continous loop to check notifications in a new thread
#     #threading.Thread(target=check_notifications_loop, args=(), daemon=True).start()


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url='/docs')


# Exception handler for pydantic validation errors
# TODO: This is a temporary solution. We should handle the errors in
#   a better way. Only request validation errors should be handled here.
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )


if __name__ == "__main__":  # debugging
    uvicorn.run(app, host="127.0.0.1", port=8000)
