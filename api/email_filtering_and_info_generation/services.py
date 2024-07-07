from datetime import datetime, timedelta
import json
import os
from typing import List
from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
# import sys
# sys.path.append('..') 
from api.email_filtering_and_info_generation.configurations.database import collection_email_msgs
from api.email_filtering_and_info_generation.configurations.database import collection_triger_events,collection_trigers,collection_readingEmailAccounts,collection_suggestions, collection_conversations, collection_issues, collection_inquiries, collection_overdue_trigger_events, collection_configurations,collection_maindashboard_trigger_event
from api.email_filtering_and_info_generation.models import Convo_summary, Email_msg, InquiryInDB, IssueInDB, Maindashboard_trig_event, Overdue_trig_event,Trigger_event,Reading_email_acc,Suggestion
from api.email_filtering_and_info_generation.schemas import individual_email_msg_serial,list_email_msg_serial
from api.email_filtering_and_info_generation.schemas import individual_trigger_serial,list_trigger_serial
from api.email_filtering_and_info_generation.schemas import individual_readingEmailAcc_serial, list_readingEmailAcc_serial
from bson import ObjectId

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from google_auth_oauthlib.flow import Flow # type: ignore
from pathlib import Path




router = APIRouter()

async def get_all_reading_accounts():
    documents = collection_readingEmailAccounts.find({}, {"_id": 0, "address": 1})
    
    all_reading_email_accs = [doc["address"] for doc in documents]
    
    return all_reading_email_accs


        



  
# to send an email msg to EmailMessages collection
async def send_email_message(email_msg_dict: Email_msg):
    try:
        # Insert the email message dictionary into the MongoDB collection
        result = collection_email_msgs.insert_one(email_msg_dict)
        
        # Return the ID of the inserted document
        return {"message": "Email message sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
# to send a suggestion to Suggestions collection
async def send_suggestion(suggestion: Suggestion):
    try:
        # Insert the suggestion dictionary into the MongoDB collection
        result = collection_suggestions.insert_one(suggestion)
        
        # Return the ID of the inserted document
        return {"message": "Suggestion sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# to send a conversation summary to Conversations collection
async def send_convo_summary(convo_summary: Convo_summary):
    try:
        # Insert the conversation summary dictionary into the MongoDB collection
        result = collection_conversations.insert_one(convo_summary.dict())
        
        # Return the ID of the inserted document
        return {"message": "Conversation summary sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def update_summary(thread_id: str, new_summary: str, new_updated_times:List[datetime]):
    result =  collection_conversations.update_one(
        {"thread_id": thread_id},
        {"$set": {"summary": new_summary, "updated_times": new_updated_times}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return {"message": "Summary updated successfully"}
    
# to send an issue to Issues collection
async def send_issue(issue: IssueInDB):
    try:
        # Insert the conversation summary dictionary into the MongoDB collection
        result = collection_issues.insert_one(issue.dict())
        
        # Return the ID of the inserted document
        return {"message": "Issue sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 



async def update_issue_status(thread_id_to_update:str, issue_convo_summary_arr:List[dict], updated_time:datetime, new_status:str, new_ongoing_status:str, sentiment_score: float, end_time_value:datetime, new_effectiveness:str, new_efficiency:str):
    try:
        # Update the document with the specified thread_id
        result = collection_issues.update_one(
            {"thread_id": thread_id_to_update},
            {"$set": {"issue_convo_summary_arr":issue_convo_summary_arr,"updated_time":updated_time,"status": new_status, 
                      "ongoing_status":new_ongoing_status, "sentiment_score":sentiment_score,
                      "end_time": end_time_value, "effectiveness":new_effectiveness, "efficiency":new_efficiency}}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# to send an inquiry to Inquiries collection
async def send_inquiry(inquiry: InquiryInDB):
    try:
        # Insert the conversation summary dictionary into the MongoDB collection
        result = collection_inquiries.insert_one(inquiry.dict())
        
        # Return the ID of the inserted document
        return {"message": "Inquiry sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    


async def update_inquiry_status(thread_id_to_update:str, new_inquiry_convo_summary:str, updated_time:datetime, new_status:str, new_ongoing_status:str, sentiment_score: float,end_time_value:datetime, new_effectiveness:str, new_efficiency:str):
    try:
        # Update the document with the specified thread_id
        result = collection_inquiries.update_one(
            {"thread_id": thread_id_to_update},
            {"$set": {"inquiry_convo_summary":new_inquiry_convo_summary, "updated_time":updated_time, 
                      "status": new_status, "ongoing_status":new_ongoing_status, "sentiment_score":sentiment_score,
                      "end_time": end_time_value, "effectiveness":new_effectiveness, "efficiency":new_efficiency}}
        )
        
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# to send a trigger event to TriggerEvents collection
async def send_trig_event(trig_event_dict: Trigger_event):
    try:
        # Insert the tig_event dictionary into the MongoDB collection
        result = collection_triger_events.insert_one(trig_event_dict)
        
        # Return the ID of the inserted document
        return {"message": "Trigger event sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

async def post_email_msg(email_msg: Email_msg):
    collection_email_msgs.insert_one(email_msg.dict())
    
    

# get all the triggers from the TriggerEvents collection

async def get_triggers_array():
    triggers_array = list_trigger_serial(collection_trigers.find())
    return triggers_array


# get all the triggers from the readingEmailAccounts collection
async def get_reading_emails_array():
    email_acc_array = list_readingEmailAcc_serial(collection_readingEmailAccounts.find())
    return email_acc_array
    

# send a new email into readingEmailAccounts collection
async def send_reading_email_account(readingEmailAcc: Reading_email_acc):
    try:
        # Insert the tig_event dictionary into the MongoDB collection
        result = collection_readingEmailAccounts.insert_one(readingEmailAcc.dict())
        
        # Return the ID of the inserted document
        return {"message": "new reading email account sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    

#-------------------------------------notification checkin database calls-----------------------------------------------------

@router.get("/info_and_retrieval/get_overall_sentiment")
async def get_overall_sentiment_value(recipient:str, intervalIndays: int):
    
    
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)
    
    # Query MongoDB for documents matching recipients
    query = {
            "recipient": recipient,
            "time": {"$gte": n_days_ago}
        }    
    results = collection_email_msgs.find(query, {"_id": 0, "our_sentiment_score": 1})
    
    # Extract our_sentiment_score values
    sentiment_scores = [doc["our_sentiment_score"] for doc in results]
    
        
    total_sentiment_score = 0
    no_of_emails = 0
    
    for sentiment_score in sentiment_scores:
        no_of_emails += 1
        total_sentiment_score = total_sentiment_score + sentiment_score
    
    print("total_sentiment_score", total_sentiment_score, "no_of_emails", no_of_emails, "email address", recipient)
    
    if no_of_emails>0:
        avg_sentiment_score = round(total_sentiment_score/no_of_emails,3)
    
        return [avg_sentiment_score, total_sentiment_score, no_of_emails]
    
    else:
        
        return 0

async def get_overdue_issues(overdue_margin_time):
    # Calculate the threshold date (start_time + 14 days)
    threshold_date = datetime.utcnow() - timedelta(days=overdue_margin_time)

    # Aggregation pipeline to filter documents with status 'ongoing' and start_time older than 14 days
    pipeline = [
        {
            "$match": {
                "status": "ongoing",
                "start_time": {"$lt": threshold_date},
                "isOverdue":False
            }
        },
        {
            "$project": {
                "_id": 0,
                "thread_id": 1,
                "recepient_email":1,
                "issue_summary":1,
                "thread_subject":1
            }
        }
    ]

    # Execute the aggregation pipeline
    result = list(collection_issues.aggregate(pipeline))
    return result

async def get_overdue_inquiries(overdue_margin_time):
    # Calculate the threshold date (start_time + 14 days)
    threshold_date = datetime.utcnow() - timedelta(days=overdue_margin_time)

    # Aggregation pipeline to filter documents with status 'ongoing' and start_time older than 14 days
    pipeline = [
        {
            "$match": {
                "status": "ongoing",
                "start_time": {"$lt": threshold_date},
                "isOverdue":False
            }
        },
        {
            "$project": {
                "_id": 0,
                "thread_id": 1,
                "recepient_email":1,
                "inquiry_summary":1,
                "thread_subject":1
            }
        }
    ]

    # Execute the aggregation pipeline
    result = list(collection_inquiries.aggregate(pipeline))
    return result


async def send_overdue_trigger_event(overdue_trigger_event: Overdue_trig_event):
    try:
        # Insert the tig_event dictionary into the MongoDB collection
        result = collection_overdue_trigger_events.insert_one(overdue_trigger_event)
        
        # Return the ID of the inserted document
        return {"message": "new overdue trigger event sent successfully", "inserted_id": str(result.inserted_id)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



async def send_main_dashboard_notification_trigger_event(maindashboard_trigger_event: Maindashboard_trig_event):
    try:
        # Insert the tig_event dictionary into the MongoDB collection
        result = collection_maindashboard_trigger_event.insert_one(maindashboard_trigger_event.dict())
        
        # Return the ID of the inserted document
        return {"message": "new overdue trigger event sent successfully", "inserted_id": str(result.inserted_id)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def getProductsList():

 result =  collection_configurations.find_one({"id": 1})
 if result:
    productsList = result.get("products",[])
    print("products List gained       :", productsList)
    return productsList
    
 else:
    print("No document found with id 1")
    return []






    