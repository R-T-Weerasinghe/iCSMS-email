from fastapi import FastAPI
# Router imports
from Routers.filter_router import filtering_router
from Routers.summaries_router import summaries_router
from Routers.analytics_router import analytics_router
from Routers.settings_router import settings_router
#

app = FastAPI()

# Router includes
email_route_prefix = "/email"
app.include_router(filtering_router, prefix=email_route_prefix)
app.include_router(summaries_router, prefix=email_route_prefix)
app.include_router(analytics_router, prefix=email_route_prefix)
app.include_router(settings_router, prefix=email_route_prefix)
#


@app.exception_handler(Exception)
async def general_exception_logger(request, exc):

    raise exc


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
