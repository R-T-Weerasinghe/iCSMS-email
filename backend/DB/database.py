#  @bekbrace
#  FARMSTACK Tutorial - Sunday 13.06.2021

# mongoDB driver
import motor.motor_asyncio
from model import Email

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017/')
database = client.emailDB
collection = database.emails


async def fetch_one_email(emailId):
    document = await collection.find_one({"emailId": emailId})
    return document


async def fetch_all_ids():
    ids = []
    cursor = collection.find({})
    async for document in cursor:
        ids.append(document["emailId"])
    return ids


async def fetch_all_emails():
    emails = []
    cursor = collection.find({})
    async for document in cursor:
        emails.append(Email(**document))
    return emails


async def create_email(email):
    document = email
    result = await collection.insert_one(document)
    return document


async def update_email(emailId, desc):
    await collection.update_one({"emailId": emailId}, {"$set": {"description": desc}})
    # set operator to update a field
    document = await collection.find_one({"emailId": emailId})
    return document


async def remove_email(emailId):
    await collection.delete_one({"emailId": emailId})
    return True
