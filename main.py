from fastapi import FastAPI
# Router imports
from Routers.email_filter_router import email_filtering_router
from Routers.email_summaries_router import email_summaries_router
from Routers.email_analytics_router import email_analytics_router
from Routers.email_settings_router import email_settings_router
#

app = FastAPI()

# Router includes
email_route_prefix = "/email"
app.include_router(email_filtering_router, prefix=email_route_prefix)
app.include_router(email_summaries_router, prefix=email_route_prefix)
app.include_router(email_analytics_router, prefix=email_route_prefix)
app.include_router(email_settings_router, prefix=email_route_prefix)
#


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
