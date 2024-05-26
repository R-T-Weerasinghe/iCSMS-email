from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
# import sys
# sys.path.append('..') 
from api.email_filtering_and_info_generation.configurations.database import collection_email_msgs
from api.email_filtering_and_info_generation.configurations.database import collection_triger_events,collection_trigers,collection_readingEmailAccounts,collection_suggestions, collection_conversations, collection_issues, collection_inquiries, collection_overdue_trigger_events
from api.email_filtering_and_info_generation.models import Convo_summary, Email_msg, Inquiry, Issue, Overdue_trig_event,Trigger_event,Reading_email_acc,Suggestion
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
    
    
    
# to send a suggestion to Suggestions collection
@router.post("/info_and_retrieval/send_suggestion")
async def send_suggestion(suggestion: Suggestion):
    try:
        # Insert the suggestion dictionary into the MongoDB collection
        result = collection_suggestions.insert_one(suggestion)
        
        # Return the ID of the inserted document
        return {"message": "Suggestion sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# to send a conversation summary to Conversations collection
@router.post("/info_and_retrieval/send_convo_summary")
async def send_convo_summary(convo_summary: Convo_summary):
    try:
        # Insert the conversation summary dictionary into the MongoDB collection
        result = collection_conversations.insert_one(convo_summary)
        
        # Return the ID of the inserted document
        return {"message": "Conversation summary sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# to send an issue to Issues collection
@router.post("/info_and_retrieval/send_issue")
async def send_issue(issue: Issue):
    try:
        # Insert the conversation summary dictionary into the MongoDB collection
        result = collection_issues.insert_one(issue)
        
        # Return the ID of the inserted document
        return {"message": "Issue sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 


@router.post("/info_and_retrieval/update_issue_status")
async def update_issue_status(thread_id_to_update:str, new_issue_convo_summary:str, new_status:str, end_time_value:datetime, new_effectiveness:str, new_efficiency:str):
    try:
        # Update the document with the specified thread_id
        result = collection_issues.update_one(
            {"thread_id": thread_id_to_update},
            {"$set": {"issue_convo_summary":new_issue_convo_summary,"status": new_status, "end_time": end_time_value, "effectiveness":new_effectiveness, "efficiency":new_efficiency}}
        )
        
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# to send an inquiry to Inquiries collection
@router.post("/info_and_retrieval/send_inquiry")
async def send_inquiry(inquiry: Inquiry):
    try:
        # Insert the conversation summary dictionary into the MongoDB collection
        result = collection_inquiries.insert_one(inquiry)
        
        # Return the ID of the inserted document
        return {"message": "Inquiry sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    

@router.post("/info_and_retrieval/update_inquiry_status")
async def update_inquiry_status(thread_id_to_update:str, new_inquiry_convo_summary:str, new_status:str, end_time_value:datetime, new_effectiveness:str, new_efficiency:str):
    try:
        # Update the document with the specified thread_id
        result = collection_inquiries.update_one(
            {"thread_id": thread_id_to_update},
            {"$set": {"inquiry_convo_summary":new_inquiry_convo_summary, "status": new_status, "end_time": end_time_value, "effectiveness":new_effectiveness, "efficiency":new_efficiency}}
        )
        
        
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
    
    

#-------------------------------------notification checkin database calls-----------------------------------------------------

@router.get("/info_and_retrieval/get_overall_sentiment/")
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
    
    #print("total_sentiment_score", total_sentiment_score, "no_of_emails", no_of_emails)
    
    if no_of_emails>0:
        avg_sentiment_score = round(total_sentiment_score/no_of_emails,3)
    
        return avg_sentiment_score
    
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
                "recepient_email":1
            }
        }
    ]

    # Execute the aggregation pipeline
    result = list(collection_issues.aggregate(pipeline))
    return result


async def send_overdue_trigger_event(overdue_trigger_event: Overdue_trig_event):
    try:
        # Insert the tig_event dictionary into the MongoDB collection
        result = collection_overdue_trigger_events.insert_one(overdue_trigger_event)
        
        # Return the ID of the inserted document
        return {"message": "new overdue trigger event sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))