import json
import os
from fastapi import HTTPException
from api.email_filtering_and_info_generation.models import Reading_email_acc
from api.v2.models.settingsModel import  EditingEmailData, EmailAcc, GetNewIntergratingEmailID, NotiSendingChannelsRecord, PutNotiSendingChannelsRecordDB, SSShiftData
from api.email_filtering_and_info_generation.services import send_reading_email_account, get_reading_emails_array
#from api.v2.dependencies.database import collection_trigers, collection_notificationSendingChannels, collection_readingEmailAccounts, collection_configurations
from api.email_filtering_and_info_generation.configurations.database import collection_trigers, collection_notificationSendingChannels, collection_readingEmailAccounts, collection_configurations
from api.email_filtering_and_info_generation.services import get_reading_emails_array
from google.auth.exceptions import DefaultCredentialsError
from google.auth.exceptions import OAuthError
from google_auth_oauthlib.flow import Flow 
# ----------------------DB API calls--------------------------------------------------------------------------------------------------------

# post a new trigger into Triggers 
from api.settings.models import Trigger

state_store = {}

def check_client_secret_validation_init_oauth_flow(client_secrets_file: str, redirect_uri: str):
    try:
        flow = Flow.from_client_secrets_file(
            client_secrets_file,
            scopes=[
                'https://www.googleapis.com/auth/gmail.readonly'
                #'https://www.googleapis.com/auth/gmail.modify',
                 #'https://www.googleapis.com/auth/gmail.settings.basic'
            ],
            redirect_uri=redirect_uri
        )
        
       

        return "success"
    except DefaultCredentialsError as e:
        print(f"Invalid client secret file: {e}")
        return "The client secret you entered is not valid. Please enter the correct client secret to complete the integration process ."
    except json.JSONDecodeError as e:
        print(f"JSON decoding failed: {e}")
        return "The client secret you entered is not valid. Please enter the correct client secret to complete the integration process "
    except OAuthError as e:
        # Catch broader OAuth errors, including those related to the redirect URI
        print(f"OAuth error: {e}")
        return "there is an error with your redirect URI. set up the above given URI correctly in your google cloud console and retry."
    except Exception as e:
        print(f"An error occurred: {e}")
        return "The client secret you have entered or the redirect URI that you have set up in the google cloud console is incorrect. Please fix the errors and retry."



def check_client_secret_validation(new_email_client_secret_content: str, id: int):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # if the following folder already doesn;t exist the following code will create it.
    new_folder_path= f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmailTemp"
    os.makedirs(new_folder_path, exist_ok=True)

    client_secrets_file = f"{new_folder_path}/client_secret.json"
    
    with open(client_secrets_file, "w") as file:
        file.write(new_email_client_secret_content)
    
    # MIGHT OCCU A BUG HERE BECAUSE THE REDIRECT ID FOR EACH EMAIL MIGHT BE DIFFERENT. Comment out the hardcoded id.
    
    redirect_uri = f'http://127.0.0.1:8000/email/info_and_retrieval/callback?id={id}'
    
    output = check_client_secret_validation_init_oauth_flow(client_secrets_file, redirect_uri)
    
    os.remove(client_secrets_file)
    
    return output

def check_aready_existing_reading_email(client_secret: str):
    id_docs = collection_readingEmailAccounts.find({}, {'id': 1})

    for doc in id_docs:
        print(doc['id'])
        file_path = f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{doc['id']}/client_secret.json"
        

        # Open and read the JSON file
        with open(file_path, 'r') as file:
            file_client_secret = file.read().strip()
        
        
        
        # Check if the client_secret from the file is equal to the passed client_secret
        if file_client_secret == client_secret:
            return True
            
    return False

def check_aready_existing_reading_email(client_secret: str):
    id_docs = collection_readingEmailAccounts.find({}, {'id': 1})

    for doc in id_docs:
        print(doc['id'])
        file_path = f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{doc['id']}/client_secret.json"
        

        # Open and read the JSON file
        with open(file_path, 'r') as file:
            file_client_secret = file.read().strip()
        
        
        
        # Check if the client_secret from the file is equal to the passed client_secret
        if file_client_secret == client_secret:
            return True
            
    return False

def check_aready_existing_reading_email_in_edit(client_secret: str, id:int):
    id_docs = collection_readingEmailAccounts.find({}, {'id': 1})

    for doc in id_docs:
        print(doc['id'])
        if not id == doc['id']:
            file_path = f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{doc['id']}/client_secret.json"
            

            # Open and read the JSON file
            with open(file_path, 'r') as file:
                file_client_secret = file.read().strip()
            
            
            
            # Check if the client_secret from the file is equal to the passed client_secret
            if file_client_secret == client_secret:
                return True
            
    return False
    
    
        


async def send_new_trigger(trigger: Trigger):
    try:
        # Insert the tig_event dictionary into the MongoDB collection
        result = collection_trigers.insert_one(trigger.dict())
        
        # Return the ID of the inserted document
        return {"message": "new reading email account sent successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
    
# update a trigger for a sentiment shift triggers form change     

async def update_triggers_ss(user_name: int, accs_to_check_ss: list[str], lowerSS_notify: bool, ss_lower_bound: float, upperSS_notify: bool, ss_upper_bound: float, is_checking_ss:bool):
    try:
        
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
 
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# post a new notisendingchannels record into NotisendingEmails collection
async def send_notificationchannels_record(new_noti_sending_email_rec: PutNotiSendingChannelsRecordDB):
    try:
            print("in here", new_noti_sending_email_rec.noti_sending_emails)
            result = collection_notificationSendingChannels.insert_one(new_noti_sending_email_rec.dict())
            print("after result")
            # if result.modified_count == 1:
            #         return {"message": "Notification sending channels updated successfully"}
            # else:
            #         print("insert failed")
            #         raise HTTPException(status_code=404, detail="Trigger not found") 
          
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
        
        print("-------------------", result.get("ss_upper_bound"))
        
        data: SSShiftData = SSShiftData(accs_to_check_ss = accs_to_check_ss, 
                           ss_lower_bound = ss_lower_bound, 
                           ss_upper_bound = ss_upper_bound,
                           is_checking_ss = is_checking_ss, 
                           is_lower_checking = is_lower_checking, 
                           is_upper_checking = is_upper_checking)

        return data
    else:
        data: SSShiftData = SSShiftData(accs_to_check_ss = [], 
                           ss_lower_bound = 0, 
                           ss_upper_bound = 0,
                           is_checking_ss = False, 
                           is_lower_checking = False, 
                           is_upper_checking = False)

        return data
    
    
# to get the criticality checking emails of a specific user from the Collection
async def get_accs_to_check_criticality(user_name: str):
    # Query MongoDB collection to find documents with the specified user_id
    result = collection_trigers.find_one({"user_name": user_name})
    if result:
        accs_to_check_overdue_emails = result.get("accs_to_check_critical_emails", [])
        return accs_to_check_overdue_emails
    else:
        return []

# to get the overdue issues checking emails of a specific user from the Collection
async def get_accs_to_check_overdue_issues(user_name: str):
    # Query MongoDB collection to find documents with the specified user_id
    result = collection_trigers.find_one({"user_name": user_name})
    if result:
        accs_to_check_overdue_emails = result.get("accs_to_check_overdue_issues", [])
        return accs_to_check_overdue_emails
    else:
        return []
    
async def get_new_intergrating_email_id(): 
        
    reading_email_acc_array = await get_reading_emails_array()
    
    
    # get the id of the new email account
    if reading_email_acc_array:
        # Find the maximum id value of the reading_email_acc_array
        max_id = max(int(d["id"]) for d in reading_email_acc_array) # type: ignore

        # Increment the id value for the new dictionary
        new_id = str(max_id + 1)
    else:
        new_id=1
    
    return GetNewIntergratingEmailID(emailID=new_id)
       
async def integrateEmail(new_email_address, new_email_nickname, new_email_client_secret_content):

    
    reading_email_acc_array = await get_reading_emails_array()
    
    
    # get the id of the new email account
    if reading_email_acc_array:
        # Find the maximum id value of the reading_email_acc_array
        max_id = max(int(d["id"]) for d in reading_email_acc_array) # type: ignore

        # Increment the id value for the new dictionary
        new_id = str(max_id + 1)
    else:
        new_id=1

    new_email_acc = Reading_email_acc(id=new_id, address=new_email_address, nickname=new_email_nickname)

    # send the new email account to the readingEmailAccounts collection
    respnse = await send_reading_email_account(new_email_acc)
    
    print(respnse)



    new_folder_path= f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{new_id}"
    os.makedirs(new_folder_path, exist_ok=True)

    file_name = f"{new_folder_path}/client_secret.json"

    # Open the file in write mode (this will create the file if it doesn't exist)
    with open(file_name, "w") as file:
        # Optionally, you can write some initial content to the file
        file.write(new_email_client_secret_content)

 
async def updateEmail(Old_email_address, new_email_address, new_email_nickname, new_email_client_secret_content):

    
    existing_doc = collection_readingEmailAccounts.find_one({"address": Old_email_address})
    if not existing_doc:
        raise HTTPException(status_code=404, detail=f"Document with address '{Old_email_address}' not found")
    
    else:
        
        folder_path= f"""api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{existing_doc["id"]}"""
        file_name = f"{folder_path}/client_secret.json"

        # Open the file in write mode (this will create the file if it doesn't exist)
        with open(file_name, "w") as file:
            # Truncate the file (delete existing content)
            file.truncate(0)
            # Write new content to the file
            file.write(new_email_client_secret_content)
            
            
        update_data = Reading_email_acc(id=existing_doc["id"], address=new_email_address, nickname=new_email_nickname)
        
        # Perform the update
        collection_readingEmailAccounts.update_one({"address": Old_email_address}, {"$set": update_data.dict()})
                


async def get_editing_email_data(selectedEmail: str):
    
    existing_doc = collection_readingEmailAccounts.find_one({"address": selectedEmail})
    
    if not existing_doc:
        raise HTTPException(status_code=404, detail=f"Document with address '{selectedEmail}' not found")
    
    else:
        
        folder_path= f"""api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{existing_doc["id"]}"""
        file_name = f"{folder_path}/client_secret.json"
        client_secret_string = ""
        try:
            with open(file_name, "r") as file:
                
                client_secret_string = file.read()
        except FileNotFoundError:
            print(f"File '{file_name}' not found")
        
        data = EditingEmailData(emailAddress=existing_doc["address"], nickName=existing_doc["nickname"], clientSecret=client_secret_string)
     
        return data
    
    
 
    
    

# -----------------------------------------------------non-API functions----------------------------------------------------------------



async def updateTriggersTableSS(username,emailAccsToCheckSS,lowerNotify, lowerSS, upperNotify, upperSS, is_checking_ss):
    
    
  
    if await check_user_name(username):
        print("checkuser name becomes true")
        await update_triggers_ss(username,emailAccsToCheckSS,lowerNotify,lowerSS,upperNotify,upperSS, is_checking_ss)
    else:    
        
        cuurentHighestTrigID = await get_highest_trigger_id()
        newtrigID = cuurentHighestTrigID+1
        SSNotify = is_checking_ss
        new_trigger = Trigger(trigger_id = newtrigID, user_name=username, is_checking_ss=is_checking_ss, accs_to_check_ss= emailAccsToCheckSS, accs_to_check_overdue_issues = [], accs_to_check_critical_emails = [] , ss_lower_bound= lowerSS, ss_upper_bound=upperSS,  is_lower_checking = lowerNotify,  is_upper_checking = upperNotify)
        
        await send_new_trigger(new_trigger)



async def updateTriggersTableOverdueIssues(username, emailAccsToCheckOverdueIssues: list[str]):
    
     if await check_user_name(username):
         await update_triggers_overdue_issues(username,emailAccsToCheckOverdueIssues)
     else:
         cuurentHighestTrigID = await get_highest_trigger_id()
         newtrigID = cuurentHighestTrigID+1
         
         new_trigger = Trigger(trigger_id = newtrigID, user_name=username, accs_to_check_ss= [], accs_to_check_overdue_issues= emailAccsToCheckOverdueIssues, accs_to_check_critical_emails=[], ss_lower_bound= None, ss_upper_bound=None,
                               is_checking_ss = False, is_lower_checking = False, is_upper_checking = False)
         
         await send_new_trigger(new_trigger)
         
        

async def updateTriggersTableCriticality(username, emailAccsToCheckCriticality):
    
     if await check_user_name(username):
         await update_triggers_criticality(username,emailAccsToCheckCriticality)
     else:
         cuurentHighestTrigID = await get_highest_trigger_id()
         newtrigID = cuurentHighestTrigID+1
         
         new_trigger = Trigger(trigger_id = newtrigID, user_name=username, accs_to_check_ss= [], accs_to_check_overdue_issues=[], accs_to_check_critical_emails = emailAccsToCheckCriticality, 
                               ss_lower_bound= None, ss_upper_bound=None,is_checking_ss = False, is_lower_checking = False, is_upper_checking = False)
         
         await send_new_trigger(new_trigger)
         
          
    


