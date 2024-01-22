#  @bekbrace
#  FARMSTACK Tutorial - Sunday 13.06.2021

from fastapi import FastAPI, HTTPException

from DB.model import Email

from DB.database import (
    fetch_one_email,
    fetch_all_ids,
    fetch_all_emails,
    create_email,
    update_email,
    remove_email,
)

# an HTTP-specific exception class  to generate exception information

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

# React runs on port 3000, so we need to allow that port to access our backend
origins = [
    "http://localhost:3000",
]

# what is a middleware?
# software that acts as a bridge between an operating system or database and applications, especially on a network.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"ServerStatus": "Active"}


@app.get("/api/email")
async def get_email():
    response = await fetch_all_emails()
    return response


@app.get("/api/email/id")
async def get_email_ids():
    response = await fetch_all_ids()
    return response


@app.get("/api/email/id/{emailId}", response_model=Email)
async def get_email_by_title(emailId):
    response = await fetch_one_email(emailId)
    if response:
        return response
    raise HTTPException(404, f"There is no email with the title {emailId}")


@app.post("/api/email/", response_model=Email)
async def post_email(email: Email):
    response = await create_email(email.model_dump())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")


@app.put("/api/email/id/{emailId}/", response_model=Email)
async def put_email(emailId: str, desc: str):
    response = await update_email(emailId, desc)
    if response:
        return response
    raise HTTPException(404, f"There is no email with the title {emailId}")


@app.delete("/api/email/id/{emailId}")
async def delete_email(emailId):
    response = await remove_email(emailId)
    if response:
        return "Successfully deleted email"
    raise HTTPException(404, f"There is no email with the title {emailId}")
