# main file that app starts with

# This has to be outside because of the way the app is structured
# Otherwise the relative imports within api/ and other modules won't work
# This is because the app is started from the root directory and python path is set to the root directory
# so all the imports can be called relative to the root directory

from fastapi import FastAPI
from api.summary.routes import router as conversation_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(conversation_router, prefix="/email")

@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url='/docs')