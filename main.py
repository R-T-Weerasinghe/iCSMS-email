# main file that app starts with

# This has to be outside because of the way the app is structured
# Otherwise the relative imports within api/ and other modules won't work
# This is because the app is started from the root directory and python path is set to the root directory
# so all the imports can be called relative to the root directory
import asyncio

from fastapi import FastAPI
from api.summary.routes import router as conversation_router
from api.email_filtering_and_info_generation.routes import router as retrieval_and_info_router
from api.settings.routes import router as settings_router
from api.dashboard.routes import router as dashboard_router
from api.email_filtering_and_info_generation.read_emails import repeat_every_10mins
from fastapi.middleware.cors import CORSMiddleware

import threading
import time


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(conversation_router, prefix="/email")
app.include_router(retrieval_and_info_router, prefix="/email")
app.include_router(settings_router,prefix="/email")
app.include_router(dashboard_router,prefix="/email")



def run_in_thread():
    asyncio.run(repeat_every_10mins())
        
# start the continous loop in a new thread
# threading.Thread(target=run_in_thread, args=(), daemon=True).start()


