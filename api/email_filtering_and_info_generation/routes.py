from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
# import sys
# sys.path.append('..') 
from api.email_filtering_and_info_generation.configurations.database import collection_email_msgs
from api.email_filtering_and_info_generation.configurations.database import collection_triger_events,collection_trigers,collection_readingEmailAccounts
from api.email_filtering_and_info_generation.models import Email_msg,Trigger_event,Reading_email_acc
from api.email_filtering_and_info_generation.schemas import individual_email_msg_serial,list_email_msg_serial
from api.email_filtering_and_info_generation.schemas import individual_trigger_serial,list_trigger_serial
from api.email_filtering_and_info_generation.schemas import individual_readingEmailAcc_serial, list_readingEmailAcc_serial
from bson import ObjectId




router = APIRouter()

# to send an email msg to EmailMessages collection
@router.post("/info_and_retrieval/send_email")
async def send_email_message(email_msg_dict: Email_msg):
    try:
        # Insert the email message dictionary into the MongoDB collection
        result = collection_email_msgs.insert_one(email_msg_dict)
        
        # Return the ID of the inserted document
        return {"message": "Email message sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# to send a trigger event to TriggerEvents collection
@router.post("/info_and_retrieval/send_trigger_event/")
async def send_trig_event(trig_event_dict: Trigger_event):
    try:
        # Insert the tig_event dictionary into the MongoDB collection
        result = collection_triger_events.insert_one(trig_event_dict)
        
        # Return the ID of the inserted document
        return {"message": "Trigger event sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



@router.post("/")
async def post_email_msg(email_msg: Email_msg):
    collection_email_msgs.insert_one(email_msg.dict())
    
    

# get all the triggers from the TriggerEvents collection

@router.get("/info_and_retrieval/get_triggers/")
async def get_triggers_array():
    triggers_array = list_trigger_serial(collection_trigers.find())
    return triggers_array


# get all the triggers from the readingEmailAccounts collection

@router.get("/info_and_retrieval/get_reading_email_accounts")
async def get_reading_emails_array():
    email_acc_array = list_readingEmailAcc_serial(collection_readingEmailAccounts.find())
    return email_acc_array
    

# send a new email into readingEmailAccounts collection
@router.post("/info_and_retrieval/send_reading_email_account/")
async def send_reading_email_account(readingEmailAcc: Reading_email_acc):
    try:
        # Insert the tig_event dictionary into the MongoDB collection
        result = collection_readingEmailAccounts.insert_one(readingEmailAcc)
        
        # Return the ID of the inserted document
        return {"message": "new reading email account sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    

    