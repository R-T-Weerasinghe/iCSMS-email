
from fastapi import APIRouter, Depends, HTTPException
from api.settings.models import IntergratingEmailData, NotiSendingChannelsRecord
from typing import Dict, Any
from api.email_filtering_and_info_generation.emailIntegration import integrateEmail
from api.email_filtering_and_info_generation.configurations.database import collection_trigers, collection_notificationSendingChannels, collection_readingEmailAccounts, collection_configurations
from api.email_filtering_and_info_generation.routes import get_reading_emails_array
from api.settings.models import Trigger
from fastapi.responses import JSONResponse
import shutil

from utils.auth import get_current_user



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
async def receive_trigger_data(trigger_data: Dict[str, Any], user=Depends(get_current_user)):
        username = user.username
        emailAccsToCheckSS =  trigger_data["emailAccsToCheckSS"]
        lowerNotify = trigger_data["lowerNotify"]
        lowerSS = trigger_data["lowerSS"]
        upperNotify = trigger_data["upperNotify"]
        upperSS = trigger_data["upperSS"]
        is_checking_ss = trigger_data["is_checking_ss"]
        
        print("Received data:", trigger_data)
        
        await updateTriggersTableSS(username,emailAccsToCheckSS,lowerNotify,lowerSS,upperNotify,upperSS, is_checking_ss)
        
        # if SS trigger is set for the first time then create a new noti_sending_channels document for that user
        if not await check_user_name_notisending(username):
            
           new_noti_sending_email_rec = NotiSendingChannelsRecord(user_name=username,is_dashboard_notifications=True, is_email_notifications = False, noti_sending_emails=[])
      
           await send_notificationchannels_record(new_noti_sending_email_rec)
        
# overdue issues triggers form listener
@router.post("/settings/receive_overdue_issue_trigger_data")
async def receive_overdue_issue_trigger_data(overdue_issues_trigger_data: Dict[str, Any]):
        userID = overdue_issues_trigger_data["userID"]
        accs_to_check_overdue_emails =  overdue_issues_trigger_data["accs_to_check_overdue_emails"]
        
        await updateTriggersTableOverdueIssues(userID, accs_to_check_overdue_emails)
        
        # if overdue issue trigger is set for the first time then create a new noti_sending_channels document for that user
        if not await check_user_name_notisending(userID):
            
           new_noti_sending_email_rec = NotiSendingChannelsRecord(user_id=userID,is_dashboard_notifications=True, is_email_notifications = False, noti_sending_emails=[])
      
           await send_notificationchannels_record(new_noti_sending_email_rec)
           


#crticality trigger form listener            
@router.post("/settings/receive_criticality_trigger_data")
async def receive_criticality_trigger_data(criti_trigger_data: Dict[str, Any]):
        userID = criti_trigger_data["userID"]
        accs_to_check_criticality =  criti_trigger_data["accs_to_check_criticality"]
        
        await updateTriggersTableCriticality(userID, accs_to_check_criticality)
        
        # if overdue issue trigger is set for the first time then create a new noti_sending_channels document for that user
        if not await check_user_name_notisending(userID):
            
           new_noti_sending_email_rec = NotiSendingChannelsRecord(user_id=userID,is_dashboard_notifications=True, is_email_notifications = False, noti_sending_emails=[])
      
           await send_notificationchannels_record(new_noti_sending_email_rec)
           
         

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
        
        
        if await check_user_name_notisending(userID):
          
            await update_noti_sending_emails(userID, dashboardChannelChecked, emailChannelChecked, notiSendingEmails)
        else:
    
           new_noti_sending_email_rec = NotiSendingChannelsRecord(user_id=userID,is_dashboard_notifications=dashboardChannelChecked, is_email_notifications = emailChannelChecked, noti_sending_emails=notiSendingEmails)
      
           await send_notificationchannels_record(new_noti_sending_email_rec)


# system configurations data form listener
@router.post("/settings/receive_system_configurations_data")
async def receive_system_configurations_data(system_config_data: Dict[str, Any]):
        overdue_margin_time = system_config_data["overdue_margin_time"]
        
        # if system_config_data["newProducts"] is not None and len(system_config_data["newProducts"]) > 0:
        #     newProducts = list(set(system_config_data["newProducts"]))
        # else:
        #     newProducts = []
        
        result = collection_configurations.find({"id":1})
        
        # if the config doc already exists
        if result:
            # combined_products_list = newProducts + result["products"]
            update_result = await collection_configurations.update_one(
            {"id": 1},
            {"$set": {"overdue_margin_time": overdue_margin_time}}
                )
        # making a new config doc
        else:
            try:
                    result = await collection_configurations.insert_one({
                        "id": 1,
                        "overdue_margin_time": overdue_margin_time
                    })
                    return {"message": "new config document inserted successfully", "inserted_id": str(result.inserted_id)}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
       
        
# listeing to removal of noti sending emails        
@router.post("/settings/remove_noti_sending_email")
async def remove_noti_sending_email(noti_sending_emails_dict: Dict[str, Any]):
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
    
# listeing to removal of products       
@router.post("/settings/remove_product")
async def remove_product(current_reading_products_dict: Dict[str, Any]):
    try:
       
        new_products_list=current_reading_products_dict["current_considering_products"]
        
        # Update the noti_sending_emails for the specified user_id
        result = collection_configurations.update_one(
            {"id": 1},
            {"$set": {"products": new_products_list}}
        )
        if result.modified_count == 1:
            return {"message": f"Products updated succesfully."}
        else:
            raise HTTPException(status_code=500, detail="Failed to update products list")
   
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

# send user role data to the frontend
@router.get("/settings/get_user_role_data")
async def get_user_role_data():
    return JSONResponse(content=data)

# send current SS checking emails of user 
@router.get("/settings/get_current_ss_checking_data")
async def get_current_ss_checking_data():
    data = await get_data_of_ss_threshold(1)
   
    return JSONResponse(content=data)

# send current criticality checking emails of user 1
@router.get("/settings/get_current_criticality_checking_emails")
async def get_criticalty_checking_emails():
    data = await get_accs_to_check_criticality(1)
    return JSONResponse(content=data)

# send current criticality checking emails of user 1
@router.get("/settings/get_current_overdue_issues_checking_emails")
async def get_current_overdue_issues_checking_emails():
    data = await get_accs_to_check_overdue_issues(1)
    return JSONResponse(content=data)


# send current notification channel data of user 1
@router.get("/settings/get_noti_channels_data")
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
    
# send system configuration data of company
@router.get("/settings/get_system_configuration_data")
async def get_system_configuration_data():
    
    result = collection_configurations.find_one({"id": 1})
    
    if result:
        formatted_result = {"overdue_margin_time":result["overdue_margin_time"]}
    else:
        formatted_result = {"overdue_margin_time":14}
    
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

async def update_triggers_ss(user_name: int, accs_to_check_ss: list[str], lowerSS_notify: bool, ss_lower_bound: int, upperSS_notify: bool, ss_upper_bound: int, is_checking_ss:bool):
    try:
        if lowerSS_notify and upperSS_notify:
            
            result = collection_trigers.update_one(
                {"user_name": user_name},
                {"$set": {
                    "accs_to_check_ss": accs_to_check_ss,
                    "ss_lower_bound": ss_lower_bound,
                    "ss_upper_bound": ss_upper_bound,
                    "is_lower_checking":lowerSS_notify,
                    "is_upper_checking":upperSS_notify,
                    "is_checking_ss":is_checking_ss
                                   
                }}
            )
        elif lowerSS_notify:
             result = collection_trigers.update_one(
                {"user_name": user_name},
                {"$set": {
                    "accs_to_check_ss": accs_to_check_ss,
                    "ss_lower_bound": ss_lower_bound,
                    "ss_upper_bound": None,
                }}
            )
        elif upperSS_notify:
              result = collection_trigers.update_one(
                {"user_name": user_name},
                {"$set": {
                    "accs_to_check_ss": accs_to_check_ss,
                    "ss_lower_bound": None,
                    "ss_upper_bound": ss_upper_bound
                }}
            )
        else:
              result = collection_trigers.update_one(
                {"user_name": user_name},
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


# update a trigger for a overdie issue triggers form change     
async def update_triggers_overdue_issues(user_name, accs_to_check_overdue_issues: list[str]):
    try:
        result = collection_trigers.update_one(
                {"user_name": user_name},
                {"$set": {
                    "accs_to_check_overdue_issues": accs_to_check_overdue_issues
                 }}
            )
        if result.modified_count == 1:
            return {"message": "Overdue Issue Trigger updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Trigger not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# update a trigger for a criticality triggers form change     
async def update_triggers_criticality(user_name, accs_to_check_critical_emails: list[str]):
    try:
        result = collection_trigers.update_one(
                {"user_name": user_name},
                {"$set": {
                    "accs_to_check_critical_emails": accs_to_check_critical_emails
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
   
   
   
   
      
   
# triggers collection user_name existence checker

async def check_user_name(user_name: str):
    try:
        # Check if the user_id is present in the collection
        user_document = collection_trigers.find_one({"user_name": user_name})
        if user_document:
            return True
        else:
            return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# NotisendingEmails collection user_id existence checker
async def check_user_name_notisending(user_name: str):
    try:
        # Check if the user_id is present in the collection
        user_document = collection_notificationSendingChannels.find_one({"user_name": user_name})
        if user_document:
            return True
        else:
            return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    

# to get the SS checking emails of a specific user from the Collection
@router.get("/settings/accs_to_check_ss/{user_id}")
async def get_data_of_ss_threshold(user_id: int):
    # Query MongoDB collection to find documents with the specified user_id
    result = collection_trigers.find_one({"user_id": user_id})
    if result:
        accs_to_check_ss = result.get("accs_to_check_ss", [])
        ss_lower_bound = result.get("ss_lower_bound")
        ss_upper_bound = result.get("ss_upper_bound")
        is_checking_ss = result.get("is_checking_ss")
        is_lower_checking = result.get("is_lower_checking")
        is_upper_checking = result.get("is_upper_checking")
        
        data = {"accs_to_check_ss":accs_to_check_ss, "ss_lower_bound":ss_lower_bound, "ss_upper_bound":ss_upper_bound,
                "is_checking_ss":is_checking_ss, "is_lower_checking":is_lower_checking, "is_upper_checking":is_upper_checking}
        
        return data
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
    
# to get the criticality checking emails of a specific user from the Collection
@router.get("/settings/accs_to_check_citicality/{user_id}")
async def get_accs_to_check_criticality(user_id: int):
    # Query MongoDB collection to find documents with the specified user_id
    result = collection_trigers.find_one({"user_id": user_id})
    if result:
        accs_to_check_overdue_emails = result.get("accs_to_check_critical_emails", [])
        return accs_to_check_overdue_emails
    else:
        raise HTTPException(status_code=404, detail="User not found")

# to get the overdue issues checking emails of a specific user from the Collection
@router.get("/settings/get_accs_to_check_overdue_issues/{user_id}")
async def get_accs_to_check_overdue_issues(user_id: int):
    # Query MongoDB collection to find documents with the specified user_id
    result = collection_trigers.find_one({"user_id": user_id})
    if result:
        accs_to_check_overdue_emails = result.get("accs_to_check_overdue_issues", [])
        return accs_to_check_overdue_emails
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
    

# -----------------------------------------------------non-API functions----------------------------------------------------------------



async def updateTriggersTableSS(username,emailAccsToCheckSS,lowerNotify, lowerSS, upperNotify, upperSS, is_checking_ss):
    
    
    
    if await check_user_name(username):
        
        await update_triggers_ss(username,emailAccsToCheckSS,lowerNotify,lowerSS,upperNotify,upperSS, is_checking_ss)
    else:    
        
        cuurentHighestTrigID = await get_highest_trigger_id()
        newtrigID = cuurentHighestTrigID+1
        
        new_trigger = Trigger(trigger_id = newtrigID, user_name=username, is_checking_ss=is_checking_ss, accs_to_check_ss= emailAccsToCheckSS, accs_to_check_overdue_issues = [], accs_to_check_critical_emails = [] , ss_lower_bound= lowerSS, ss_upper_bound=upperSS,  is_lower_checking = lowerNotify,  is_upper_checking = upperNotify)
        
        await send_new_trigger(new_trigger.dict())



async def updateTriggersTableOverdueIssues(username, emailAccsToCheckOverdueIssues: list[str]):
    
     if await check_user_name(username):
         await update_triggers_overdue_issues(username,emailAccsToCheckOverdueIssues)
     else:
         cuurentHighestTrigID = await get_highest_trigger_id()
         newtrigID = cuurentHighestTrigID+1
         
         new_trigger = Trigger(trigger_id = newtrigID, user_name=username, accs_to_check_ss= [], accs_to_check_overdue_issues= emailAccsToCheckOverdueIssues, accs_to_check_critical_emails=[], ss_lower_bound= None, ss_upper_bound=None)
         
         await send_new_trigger(new_trigger.dict())
         
        

async def updateTriggersTableCriticality(username, emailAccsToCheckCriticality):
    
     if await check_user_name(username):
         await update_triggers_criticality(username,emailAccsToCheckCriticality)
     else:
         cuurentHighestTrigID = await get_highest_trigger_id()
         newtrigID = cuurentHighestTrigID+1
         
         new_trigger = Trigger(trigger_id = newtrigID, user_name=username, accs_to_check_ss= [], accs_to_check_overdue_issues=[], accs_to_check_critical_emails = emailAccsToCheckCriticality, ss_lower_bound= None, ss_upper_bound=None)
         
         await send_new_trigger(new_trigger.dict())
         
          
    
