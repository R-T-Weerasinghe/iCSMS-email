from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
# import sys
# sys.path.append('..') 
from api.email_filtering_and_info_generation.configurations.database import collection_email_msgs
from api.email_filtering_and_info_generation.configurations.database import collection_triger_events,collection_trigers
from api.email_filtering_and_info_generation.models.email_msg import Email_msg
from api.email_filtering_and_info_generation.models.trigger_event import Trigger_event
from api.email_filtering_and_info_generation.schema.schemas import individual_email_msg_serial,list_email_msg_serial
from api.email_filtering_and_info_generation.schema.schemas import individual_trigger_serial,list_trigger_serial
from bson import ObjectId




router = APIRouter()

# to send an email msg to EmailMessages collection
@router.post("/send_email_message/")
async def send_email_message(email_msg_dict: Email_msg):
    try:
        # Insert the email message dictionary into the MongoDB collection
        result = collection_email_msgs.insert_one(email_msg_dict)
        
        # Return the ID of the inserted document
        return {"message": "Email message sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# to send a trigger event to TriggerEvents collection
@router.post("/send_trigger_event/")
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
    
    


@router.get("/get_triggers/")
async def get_triggers_array():
    triggers_array = list_trigger_serial(collection_trigers.find())
    return triggers_array
    
    