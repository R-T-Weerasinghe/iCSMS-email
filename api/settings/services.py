from fastapi import HTTPException
from api.settings.models import  EmailAcc, NotiSendingChannelsRecord, SSShiftData
from api.email_filtering_and_info_generation.emailIntegration import integrateEmail
from api.email_filtering_and_info_generation.configurations.database import collection_trigers, collection_notificationSendingChannels, collection_readingEmailAccounts, collection_configurations
from api.email_filtering_and_info_generation.services import get_reading_emails_array

# ----------------------DB API calls--------------------------------------------------------------------------------------------------------



# post a new trigger into Triggers 
from api.settings.models import Trigger


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

async def update_noti_sending_emails(user_name: str, is_dashboard_notifications: bool, is_email_notifications: bool, new_noti_sending_email: list[str]):
    try:
        
        user = collection_notificationSendingChannels.find_one({"user_name": user_name})
        if user:
                existing_emails = user.get("noti_sending_emails", [])
                combined_emails = existing_emails + new_noti_sending_email


                result = collection_notificationSendingChannels.update_one(
                {"user_name": user_name},
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
async def get_data_of_ss_threshold(user_name: str):
    # Query MongoDB collection to find documents with the specified user_id
    result = collection_trigers.find_one({"user_name": user_name})
    if result:
        accs_to_check_ss_string_array = result.get("accs_to_check_ss", [])
        
        accs_to_check_ss = [EmailAcc(address=email) for email in accs_to_check_ss_string_array]
        ss_lower_bound = result.get("ss_lower_bound")
        ss_upper_bound = result.get("ss_upper_bound")
        is_checking_ss = result.get("is_checking_ss")
        is_lower_checking = result.get("is_lower_checking")
        is_upper_checking = result.get("is_upper_checking")
        
        data_dict = {"accs_to_check_ss":accs_to_check_ss, "ss_lower_bound":ss_lower_bound, "ss_upper_bound":ss_upper_bound,
                "is_checking_ss":is_checking_ss, "is_lower_checking":is_lower_checking, "is_upper_checking":is_upper_checking}
        data = SSShiftData(**data_dict)
        return data
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
    
# to get the criticality checking emails of a specific user from the Collection
async def get_accs_to_check_criticality(user_name: str):
    # Query MongoDB collection to find documents with the specified user_id
    result = collection_trigers.find_one({"user_name": user_name})
    if result:
        accs_to_check_overdue_emails = result.get("accs_to_check_critical_emails", [])
        return accs_to_check_overdue_emails
    else:
        raise HTTPException(status_code=404, detail="User not found")

# to get the overdue issues checking emails of a specific user from the Collection
async def get_accs_to_check_overdue_issues(user_name: str):
    # Query MongoDB collection to find documents with the specified user_id
    result = collection_trigers.find_one({"user_name": user_name})
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
         
          
    


