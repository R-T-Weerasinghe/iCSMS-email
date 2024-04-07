# database calls

# example 

# from pymongo import MongoClient
# from motor.motor_asyncio import AsyncIOMotorClient
# from .mongodb import MongoDBSettings

# class Database:
#     def __init__(self, settings: MongoDBSettings):
#         self.client = MongoClient(settings.mongo_uri)
#         self.db = self.client[settings.db_name]

#     def get_collection(self, collection_name):
#         return self.db[collection_name]

#     def close(self):
#         self.client.close()

# async def get_async_database(settings: MongoDBSettings) -> AsyncIOMotorClient: # type: ignore
#     client: AsyncIOMotorClient = AsyncIOMotorClient(settings.mongo_uri) # type: ignore
#     db = client[settings.db_name]
#     return db

# end of example 

from .mongodb import mongo
from .pipelines import pl_conversations

def get_conversations():
    collection = mongo.get_collection("Conversations")
    return list(collection.aggregate(pl_conversations))
