from pymongo import MongoClient

#client = MongoClient("mongodb+srv://raninduharischandra12:Ruh53232@cluster0.ahtrzip.mongodb.net/?retryWrites=true&w=majority")

client = MongoClient("mongodb+srv://RaninduDBAdmin:kmHSROTUzj6keMhO@email.vm8njwj.mongodb.net/")




db = client["EmailDB"]

collection_email_msgs = db['EmailMessages']
collection_triger_events = db['TriggerEvents']
collection_trigers = db['Triggers']