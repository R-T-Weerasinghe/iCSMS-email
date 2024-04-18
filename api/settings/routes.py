
from fastapi import APIRouter, HTTPException
from api.settings.models import IntergratingEmailData, NotiSendingChannelsRecord
from typing import Dict, Any
from api.email_filtering_and_info_generation.emailIntegration import integrateEmail
from api.email_filtering_and_info_generation.configurations.database import collection_trigers, collection_notificationSendingChannels, collection_readingEmailAccounts
from api.email_filtering_and_info_generation.routes import get_reading_emails_array
from api.settings.models import Trigger
from fastapi.responses import JSONResponse
import shutil



router = APIRouter()


# ----------------------frontend API calls--------------------------------------------------------------------------------------------------------

# email integration form listener
@router.post("/settings/receive_email_data")
async def receive_email_data(email_data: Dict[str, Any]):
    # Access the email data sent from Angular
    
    print("Received data:", email_data)
    email_address = email_data["emailAddress"]
    nick_name = email_data["nickName"]
    client_secret=email_data["clientSecret"]
    
    await integrateEmail(email_address,nick_name, client_secret)

    return {"message": "Email data received successfully"}


# sentiment shift triggers form listener
@router.post("/settings/receive_trigger_data")
async def receive_trigger_data(trigger_data: Dict[str, Any]):
        userID = trigger_data["userID"]
        emailAccsToCheckSS =  trigger_data["emailAccsToCheckSS"]
        lowerNotify = trigger_data["lowerNotify"]
        lowerSS = trigger_data["lowerSS"]
        upperNotify = trigger_data["upperNotify"]
        upperSS = trigger_data["upperSS"]
        
        print("Received data:", trigger_data)
        
        await updateTriggersTableSS(userID,emailAccsToCheckSS,lowerNotify,lowerSS,upperNotify,upperSS)
        
# criticality triggers form listener
@router.post("/settings/receive_criticality_trigger_data")
async def receive_criticality_trigger_data(criti_trigger_data: Dict[str, Any]):
        userID = criti_trigger_data["userID"]
        emailAccsToCheckCriticality =  criti_trigger_data["emailAccsToCheckCriticality"]
        
        await updateTriggersTableCriticality(userID, emailAccsToCheckCriticality)

# notifications channels form listener
@router.post("/settings/receive_notifications_channel_data")
async def receive_notification_channel_data(noti_channel_data: Dict[str, Any]):
        userID = noti_channel_data['userID']
        dashboardChannelChecked=noti_channel_data["dashboardChannelChecked"]
        emailChannelChecked= noti_channel_data["emailChannelChecked"]
        if noti_channel_data["notiSendingEmails"] is not None and len(noti_channel_data["notiSendingEmails"]) > 0:
            notiSendingEmails = list(set(noti_channel_data["notiSendingEmails"]))
        else:
            notiSendingEmails = []
      
        print(userID, dashboardChannelChecked, emailChannelChecked, notiSendingEmails)
        
        
        if await check_user_id_notisending(userID):
          
            await update_noti_sending_emails(userID, dashboardChannelChecked, emailChannelChecked, notiSendingEmails)
        else:
    
           new_noti_sending_email_rec = NotiSendingChannelsRecord(user_id=userID,is_dashboard_notifications=dashboardChannelChecked, is_email_notifications = emailChannelChecked, noti_sending_emails=notiSendingEmails)
      
           await send_notificationchannels_record(new_noti_sending_email_rec)
        
        
# listeing to removal of noti sedning emails        
@router.post("/settings/remove_noti_sending_email/{user_id}")
async def remove_noti_sending_email(user_id: int, noti_sending_emails_dict: Dict[str, Any]):
    try:
        existing_record = collection_notificationSendingChannels.find_one({"user_id": user_id})
        noti_sending_emails=noti_sending_emails_dict["noti_sending_emails"]
        if existing_record:
        # Update the noti_sending_emails for the specified user_id
            result = collection_notificationSendingChannels.update_one(
                {"user_id": user_id},
                {"$set": {"noti_sending_emails": noti_sending_emails}}
            )
            if result.modified_count == 1:
                return {"message": f"Noti sending emails updated successfully for user {user_id}"}
            else:
                raise HTTPException(status_code=500, detail="Failed to update noti sending emails")
        else:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    except Exception as e:
        # If an error occurs, raise an HTTPException with status code 500
        raise HTTPException(status_code=500, detail=str(e))
    
# listeing to removal of current reading emails        
@router.post("/settings/remove_reading_email")
async def remove_reading_email(removing_email_dict: Dict[str, Any]):
    try:
        
        removing_email=removing_email_dict["removing_email"]
        print(removing_email)
        existing_one = collection_readingEmailAccounts.find_one({"address": removing_email})
        existing_id = existing_one["id"]
        result = collection_readingEmailAccounts.delete_one({"address": removing_email})
        
        new_folder_path= f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{existing_id}"
        shutil.rmtree(new_folder_path)
    
    except Exception as e:
        # If an error occurs, raise an HTTPException with status code 500
        raise HTTPException(status_code=500, detail=str(e))


# send current reading emails to frontend   
@router.get("/settings/get_current_reading_emails")
async def get_data():
    data = await get_reading_emails_array()
    return JSONResponse(content=data)

# send current SS checking emails of user 1
@router.get("/settings/get_current_ss_checking_emails")
async def get_ss_checking_emails():
    data = await get_accs_to_check_ss(1)
    return JSONResponse(content=data)

# send current criticality checking emails of user 1
@router.get("/settings/get_current_criticality_checking_emails")
async def get_criticalty_checking_emails():
    data = await get_accs_to_check_criticality(1)
    return JSONResponse(content=data)


# send current notification channel data of user 1
@router.get("/settings/get_noti_channels_data/1")
async def get_noti_channels_data():
    print("it came here")
    result = collection_notificationSendingChannels.find_one({"user_id": 1})
    if result:
        formatted_result = {
        'user_id': result['user_id'],
        'is_dashboard_notifications': result['is_dashboard_notifications'],
        'is_email_notifications': result['is_email_notifications'],
        'noti_sending_emails': result['noti_sending_emails']
        }
        return JSONResponse(content=formatted_result)
    else:
         formatted_result = {
        'user_id': -1,
        'is_dashboard_notifications': False,
        'is_email_notifications': False,
        'noti_sending_emails': []
        }   
         return JSONResponse(content=formatted_result)
    


# ----------------------DB API calls--------------------------------------------------------------------------------------------------------



# psot a new trigger into Triggers 
@router.post("/settings/send_triggers")
async def send_new_trigger(trigger: Trigger):
    try:
        # Insert the tig_event dictionary into the MongoDB collection
        result = collection_trigers.insert_one(trigger.dict())
        
        # Return the ID of the inserted document
        return {"message": "new reading email account sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
    
# update a trigger for a sentiment shift triggers form change     
@router.put("/update_triggers_ss/{user_id}")
async def update_triggers_ss(user_id: int, accs_to_check_ss: list[str], lowerSS_notify: bool, ss_lower_bound: int, upperSS_notify: bool, ss_upper_bound: int):
    try:
        if lowerSS_notify and upperSS_notify:
            
            result = collection_trigers.update_one(
                {"user_id": user_id},
                {"$set": {
                    "accs_to_check_ss": accs_to_check_ss,
                    "ss_lower_bound": ss_lower_bound,
                    "ss_upper_bound": ss_upper_bound,
                    
                    
                }}
            )
        elif lowerSS_notify:
             result = collection_trigers.update_one(
                {"user_id": user_id},
                {"$set": {
                    "accs_to_check_ss": accs_to_check_ss,
                    "ss_lower_bound": ss_lower_bound,
                    "ss_upper_bound": None,
                }}
            )
        elif upperSS_notify:
              result = collection_trigers.update_one(
                {"user_id": user_id},
                {"$set": {
                    "accs_to_check_ss": accs_to_check_ss,
                    "ss_lower_bound": None,
                    "ss_upper_bound": ss_upper_bound
                }}
            )
        else:
              result = collection_trigers.update_one(
                {"user_id": user_id},
                {"$set": {
                    "accs_to_check_ss": [],
                    "ss_lower_bound": None,
                    "ss_upper_bound": None
                }}
            )
            
              
        if result.modified_count == 1:
            return {"message": "Trigger updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Trigger not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# update a trigger for a criticality triggers form change     
@router.put("/update_triggers_criticality/{user_id}")
async def update_triggers_criticality(user_id: int, accs_to_check_criticality: list[str]):
    try:
        result = collection_trigers.update_one(
                {"user_id": user_id},
                {"$set": {
                    "accs_to_check_criticality": accs_to_check_criticality
                 }}
            )
        if result.modified_count == 1:
            return {"message": "Crticality Trigger updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Trigger not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# post a new notisendingchannels record into NotisendingEmails collection
@router.post("/settings/send_notificationchannels_record")
async def send_notificationchannels_record(new_noti_sending_email_rec: NotiSendingChannelsRecord):
    try:
            print("in here", new_noti_sending_email_rec.noti_sending_emails)
            result = collection_notificationSendingChannels.insert_one(new_noti_sending_email_rec.dict())
            print("after result")
            if result.modified_count == 1:
                    return {"message": "Notification sending channels updated successfully"}
            else:
                    print("insert failed")
                    raise HTTPException(status_code=404, detail="Trigger not found") 
          
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
      

# update a notiSendingEmails collection after a noti channel form change     
@router.put("/update_noti_sending_emails/{user_id}")
async def update_noti_sending_emails(user_id: int, is_dashboard_notifications: bool, is_email_notifications: bool, new_noti_sending_email: list[str]):
    try:
        
        user = collection_notificationSendingChannels.find_one({"user_id": user_id})
        if user:
                existing_emails = user.get("noti_sending_emails", [])
                combined_emails = existing_emails + new_noti_sending_email


                result = collection_notificationSendingChannels.update_one(
                {"user_id": user_id},
                {"$set": {
                    "is_dashboard_notifications":is_dashboard_notifications,
                    "is_email_notifications":is_email_notifications,
                    "noti_sending_emails": combined_emails}}
                )
                
                if result.modified_count == 1:
                    return {"message": "Crticality Trigger updated successfully"}
                else:
                    raise HTTPException(status_code=404, detail="Trigger not found")                
          
            
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    

# get the current highest trigger_id
@router.get("/settings/highest_trigger_id")
async def get_highest_trigger_id():
    try:
        # Find the document with the highest trigger_id
        highest_trigger_id_document = collection_trigers.find_one(sort=[("trigger_id", -1)])
        if highest_trigger_id_document:
            highest_trigger_id = highest_trigger_id_document.get("trigger_id")
            return highest_trigger_id
        else:
            raise HTTPException(status_code=404, detail="No trigger IDs found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   
   
   
   
      
   
# triggers collection user_id existence checker
@router.get("/settings/check_user_id/{user_id}")
async def check_user_id(user_id: int):
    try:
        # Check if the user_id is present in the collection
        user_document = collection_trigers.find_one({"user_id": user_id})
        if user_document:
            return True
        else:
            return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# NotisendingEmails collection user_id existence checker
@router.get("/settings/check_user_id_notisending/{user_id}")
async def check_user_id_notisending(user_id: int):
    try:
        # Check if the user_id is present in the collection
        user_document = collection_notificationSendingChannels.find_one({"user_id": user_id})
        if user_document:
            return True
        else:
            return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    

# to get the SS checking emails of a specific user from the Collection
@router.get("/settings/accs_to_check_ss/{user_id}")
async def get_accs_to_check_ss(user_id: int):
    # Query MongoDB collection to find documents with the specified user_id
    result = collection_trigers.find_one({"user_id": user_id})
    if result:
        accs_to_check_ss = result.get("accs_to_check_ss", [])
        return accs_to_check_ss
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
    
# to get the criticality checking emails of a specific user from the Collection
@router.get("/settings/accs_to_check_citicality/{user_id}")
async def get_accs_to_check_criticality(user_id: int):
    # Query MongoDB collection to find documents with the specified user_id
    result = collection_trigers.find_one({"user_id": user_id})
    if result:
        accs_to_check_criticality = result.get("accs_to_check_criticality", [])
        return accs_to_check_criticality
    else:
        raise HTTPException(status_code=404, detail="User not found")



# -----------------------------------------------------non-API functions----------------------------------------------------------------



async def updateTriggersTableSS(userID,emailAccsToCheckSS,lowerNotify, lowerSS, upperNotify, upperSS):
    
    
    
    if await check_user_id(userID):
        
        await update_triggers_ss(userID,emailAccsToCheckSS,lowerNotify,lowerSS,upperNotify,upperSS)
    else:    
        
        cuurentHighestTrigID = await get_highest_trigger_id()
        newtrigID = cuurentHighestTrigID+1
        
        new_trigger = Trigger(trigger_id = newtrigID, user_id=userID, accs_to_check_ss= emailAccsToCheckSS, accs_to_check_criticality = [], ss_lower_bound= lowerSS, ss_upper_bound=upperSS)
        
        await send_new_trigger(new_trigger.dict())



async def updateTriggersTableCriticality(userID, emailAccsToCheckCriticality):
    
     if await check_user_id(userID):
         await update_triggers_criticality(userID,emailAccsToCheckCriticality)
     else:
         cuurentHighestTrigID = await get_highest_trigger_id()
         newtrigID = cuurentHighestTrigID+1
         
         new_trigger = Trigger(trigger_id = newtrigID, user_id=userID, accs_to_check_ss= [], accs_to_check_criticality = emailAccsToCheckCriticality, ss_lower_bound= None, ss_upper_bound=None)
         
         await send_new_trigger(new_trigger.dict())
         
        
     
    
