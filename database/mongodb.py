# mongodb configurations

# example

# from pydantic import BaseSettings

# class MongoDBSettings(BaseSettings):
#     mongo_uri: str = "mongodb://localhost:27017/"
#     db_name: str = "email_analysis_db"

# end of example 

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoDB:
    def __init__(self, url, db_name):
        self.client = MongoClient(url)
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def check_connection(self):
        try:
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            print("MongoDB connection successful")
            return True
        except ConnectionFailure:
            print("MongoDB connection failed")
            return False

# Example MongoDB configuration
mongo_uri = "mongodb+srv://RaninduDBAdmin:kmHSROTUzj6keMhO@email.vm8njwj.mongodb.net/"
mongo_db = "EmailDB"
mongo = MongoDB(mongo_uri, mongo_db)

# Check connection at startup
mongo.check_connection()