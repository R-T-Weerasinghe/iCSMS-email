
from fastapi import APIRouter, Depends, HTTPException, Query
from api.email_authorization.services import login_async
from api.v2.models.settingsModel import Trigger,DeleteNotiSendingEmail, DeleteReadingEmail, EditingEmailData, EmailAcc, EmailAccWithNickName, EmailINtegrationPostResponseMessage, GetNewIntergratingEmailID, IntergratingEmailData, IssueInqTypeData, NotiSendingChannelsRecord, PostEditingEmail, PostNewIntegratingEmail, PostingCriticalityData, PostingNotiSendingChannelsRecord, PostingOverdueIssuesData, PutNotiSendingChannelsRecordDB, SSShiftData, SendSystemConfigData, UserRoleResponse
from typing import Dict, Any, List
#from api.email_filtering_and_info_generation.configurations.database import collection_trigers, collection_notificationSendingChannels, collection_readingEmailAccounts, collection_configurations
from api.email_filtering_and_info_generation.configurations.database import collection_trigers, collection_notificationSendingChannels, collection_readingEmailAccounts, collection_configurations

from api.email_filtering_and_info_generation.services import get_reading_emails_array
from fastapi.responses import JSONResponse
import shutil

from api.v2.services import settingsService as services
from utils.auth import get_current_user




router = APIRouter()


# ----------------------frontend API calls--------------------------------------------------------------------------------------------------------

# email integration form listener
@router.post("/settings/receive_email_data")
async def receive_email_data(email_data: PostNewIntegratingEmail):
    # Access the email data sent from Angular
    
    print("Received data:", email_data)
    email_id = email_data.emailID
    email_address = email_data.emailAddress
    nick_name = email_data.nickName
    client_secret=email_data.clientSecret
    already_exits = services.check_aready_existing_reading_email(client_secret)
    print("already_exits",already_exits)
    if not already_exits:
        result = services.check_client_secret_validation(client_secret, email_id)
        
        if  result == "success":
            await services.integrateEmail(email_address,nick_name, client_secret)
            return EmailINtegrationPostResponseMessage(message = "intergration complete")
        else:
            return EmailINtegrationPostResponseMessage(message = result)
    else:
        return EmailINtegrationPostResponseMessage(message = "This email address is already being read. Please enter a different email address.")

    

  

# listen to rading email account edits
@router.post("/settings/receive_email_edit_data")
async def receive_email_edit_data(email_data: PostEditingEmail):

    old_email_address = email_data.oldEmailAddress
    email_address = email_data.editedEmailAddress
    nick_name = email_data.nickName
    client_secret=email_data.clientSecret
    print("old email address", old_email_address)
    doc = collection_readingEmailAccounts.find_one({"address": old_email_address}, {"id": 1})
    
    already_exits = services.check_aready_existing_reading_email_in_edit(client_secret, doc['id'])
    if not already_exits:
        result = services.check_client_secret_validation(client_secret, doc['id'])
        
        if  result == "success":
            await services.updateEmail(old_email_address,email_address,nick_name, client_secret)
            return EmailINtegrationPostResponseMessage(message = "edit complete")
        else:
            return EmailINtegrationPostResponseMessage(message = result)
        
    else:
        return EmailINtegrationPostResponseMessage(message = "This email address is already being read. Please enter a different email address.")

   



# sentiment shift triggers form listener
@router.post("/settings/receive_trigger_data")
async def receive_trigger_data(trigger_data:SSShiftData, user=Depends(get_current_user)):
        username = user.username
        emailAccsToCheckSS =  [email.address for email in trigger_data.accs_to_check_ss]
        lowerNotify = trigger_data.is_lower_checking
        lowerSS = trigger_data.ss_lower_bound
        upperNotify = trigger_data.is_upper_checking
        upperSS = trigger_data.ss_upper_bound
        is_checking_ss = trigger_data.is_checking_ss
        
        print("Received data:", trigger_data)
        
        await services.updateTriggersTableSS(username,emailAccsToCheckSS,lowerNotify,lowerSS,upperNotify,upperSS, is_checking_ss)
        
        # if SS trigger is set for the first time then create a new noti_sending_channels document for that user
        if not await services.check_user_name_notisending(username):
           
           new_noti_sending_email_rec = NotiSendingChannelsRecord(user_name=username,is_dashboard_notifications=True, is_email_notifications = False, noti_sending_emails=[])
      
           await services.send_notificationchannels_record(new_noti_sending_email_rec)
        
# overdue issues triggers form listener
@router.post("/settings/receive_overdue_issue_trigger_data")
async def receive_overdue_issue_trigger_data(overdue_issues_trigger_data: PostingOverdueIssuesData,  user=Depends(get_current_user)):
        username = user.username 
        accs_to_check_overdue_emails =  overdue_issues_trigger_data.accs_to_check_overdue_emails
        
        
        await services.updateTriggersTableOverdueIssues(username, accs_to_check_overdue_emails)
        
        # if overdue issue trigger is set for the first time then create a new noti_sending_channels document for that user
        if not await services.check_user_name_notisending(username):
            
           new_noti_sending_email_rec = NotiSendingChannelsRecord(user_name=username,is_dashboard_notifications=True, is_email_notifications = False, noti_sending_emails=[])
      
           await services.send_notificationchannels_record(new_noti_sending_email_rec)
           


#crticality trigger form listener            
@router.post("/settings/receive_criticality_trigger_data")
async def receive_criticality_trigger_data(criti_trigger_data: PostingCriticalityData, user=Depends(get_current_user)):
        username = user.username 
        accs_to_check_criticality =  criti_trigger_data.accs_to_check_criticality
        
        print(criti_trigger_data)
        await services.updateTriggersTableCriticality(username, accs_to_check_criticality)
        
        # if overdue issue trigger is set for the first time then create a new noti_sending_channels document for that user
        if not await services.check_user_name_notisending(username):
            
           new_noti_sending_email_rec = NotiSendingChannelsRecord(user_name=username,is_dashboard_notifications=True, is_email_notifications = False, noti_sending_emails=[])
      
           await services.send_notificationchannels_record(new_noti_sending_email_rec)
           
         

# notifications channels form listener
@router.post("/settings/receive_notifications_channel_data")
async def receive_notification_channel_data(noti_channel_data: PostingNotiSendingChannelsRecord, user=Depends(get_current_user)):
    try:
        username = user.username
        dashboardChannelChecked = noti_channel_data.is_dashboard_notifications
        emailChannelChecked = noti_channel_data.is_email_notifications
        
        if noti_channel_data.noti_sending_emails is not None and len(noti_channel_data.noti_sending_emails) > 0:
            notiSendingEmails = list(set(noti_channel_data.noti_sending_emails))
        else:
            notiSendingEmails = []
        
        print(username, dashboardChannelChecked, emailChannelChecked, notiSendingEmails)
        
        if await services.check_user_name_notisending(username):
            await services.update_noti_sending_emails(username, dashboardChannelChecked, emailChannelChecked, notiSendingEmails)
        else:
            new_noti_sending_email_rec = PutNotiSendingChannelsRecordDB(
                user_name=username,
                is_dashboard_notifications=dashboardChannelChecked,
                is_email_notifications=emailChannelChecked,
                noti_sending_emails=notiSendingEmails
            )
            await services.send_notificationchannels_record(new_noti_sending_email_rec)
    
    except Exception as e:
        # Log the exception (optional)
        print(f"An error occurred: {e}")
        
        # Raise an HTTP exception with a 400 status code and the error message
        raise HTTPException(status_code=400, detail=str(e))


# system configurations data form listener
@router.post("/settings/receive_system_configurations_data")
async def receive_system_configurations_data(system_config_data: SendSystemConfigData):
    try:
            overdue_margin_time = system_config_data.overdue_margin_time
            
            result = collection_configurations.find({"id":1})
            
            # if the config doc already exists
            if result:
         
                update_result = collection_configurations.update_one(
                {"id": 1},
                {"$set": {"overdue_margin_time": overdue_margin_time}}
                    )
            # making a new config doc
            else:
                try:
                        result = collection_configurations.insert_one({
                            "id": 1,
                            "overdue_margin_time": overdue_margin_time
                        })
                        return {"message": "new config document inserted successfully", "inserted_id": str(result.inserted_id)}
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            return {"message": "new config document inserted successfully"}
    
    except Exception as e:
        # Log the exception (optional)
        print(f"An error occurred: {e}")
        
        # Raise an HTTP exception with a 400 status code and the error message
        raise HTTPException(status_code=400, detail=str(e))



# issueninqyiryTypesConfigurations form listener     
@router.post("/settings/receive_issue_inq_type_data")
async def receive_issue_inq_type_data(iss_inq_type_data: IssueInqTypeData):  
    try:
        print("recieved issue inq type data", iss_inq_type_data)
        updated_issue_types_to_check = iss_inq_type_data.issue_types_to_check
        updated_inquiry_types_to_check = iss_inq_type_data.inquiry_types_to_check           
        
        result = collection_configurations.find({"id":3})  
        
        # if the config doc already exists
        if result:
        
            collection_configurations.update_one(
            {"id": 3},
            {"$set": {"issue_types": updated_issue_types_to_check, "inquiry_types":updated_inquiry_types_to_check}}
                )
            
        # making a new config doc
        else:
            try:
                    result = collection_configurations.insert_one({
                        "id": 3,
                        "issue_types": updated_issue_types_to_check,
                        "inquiry_types": updated_issue_types_to_check
                    })
                    return {"message": "new issue and inquiry type doc inserted successfully", "inserted_id": str(result.inserted_id)}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
    except Exception as e:
        # Log the exception (optional)
        print(f"An error occurred: {e}")
        
        # Raise an HTTP exception with a 400 status code and the error message
        raise HTTPException(status_code=400, detail=str(e))    
    
        
# listeing to removal of noti sending emails        
@router.post("/settings/remove_noti_sending_email")
async def remove_noti_sending_email(noti_sending_emails_dict: DeleteNotiSendingEmail, user=Depends(get_current_user)):
    try:
        username = user.username 
        existing_record = collection_notificationSendingChannels.find_one({"user_name": username})
        noti_sending_emails=noti_sending_emails_dict.noti_sending_emails
        if existing_record:
        # Update the noti_sending_emails for the specified user_id
            result = collection_notificationSendingChannels.update_one(
                {"user_name": username},
                {"$set": {"noti_sending_emails": noti_sending_emails}}
            )
            if result.modified_count == 1:
                return {"message": f"Noti sending emails updated successfully for user {username}"}
            else:
                raise HTTPException(status_code=500, detail="Failed to update noti sending emails")
        else:
            raise HTTPException(status_code=404, detail=f"User {username} not found")
    except Exception as e:
        # If an error occurs, raise an HTTPException with status code 500
        raise HTTPException(status_code=500, detail=str(e))
    

    
# listeing to removal of current reading emails        
@router.post("/settings/remove_reading_email")
async def remove_reading_email(removing_email_dict: DeleteReadingEmail):
    try:
        
        removing_email=removing_email_dict.removing_email
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
@router.get("/settings/get_current_reading_emails", response_model=List[EmailAccWithNickName])
async def get_data():
    try:
        reading_email_acc_model_data_array = await get_reading_emails_array()
        data = [EmailAccWithNickName(address=item["address"], nickname=item["nickname"]) for item in reading_email_acc_model_data_array]
        return data
    except ValueError as ve:
        print(f"ValueError occurred: {ve}")
        raise HTTPException(status_code=400, detail="Invalid data format.")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while retrieving data.")

# send editing email data to frontend   
@router.get("/settings/get_editing_email_data", response_model=EditingEmailData)
async def get_editing_email_data(selectedEmail: str = Query(...)):
    try:
        data: EditingEmailData = await services.get_editing_email_data(selectedEmail)
        return data
    except ValueError as ve:
        # Handle specific exceptions like ValueError if needed
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Log the exception (optional)
        print(f"An error occurred: {e}")
        
        # Raise an HTTP exception with a 500 status code and the error message
        raise HTTPException(status_code=500, detail="An internal error occurred while retrieving email data.")


# send user role data to the frontend
@router.get("/settings/get_user_role_data", response_model=UserRoleResponse)
async def get_user_role_data(user=Depends(get_current_user)):
    try:
        userroles = user.roles
        if "Admin" in userroles:
            data = UserRoleResponse(isAdmin=True)
        else:
            data = UserRoleResponse(isAdmin=False)
            
        return data
    except AttributeError as ae:
        # This exception handles cases where `user` or `user.roles` might not be defined correctly
        print(f"AttributeError occurred: {ae}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving user roles")
    except HTTPException as he:
        # Re-raise HTTPExceptions to return the appropriate response to the client
        raise he
    except Exception as e:
        # Catch all other exceptions and log them
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

# send current SS checking emails of user 
@router.get("/settings/get_current_ss_checking_data", response_model=SSShiftData)
async def get_current_ss_checking_data(user=Depends(get_current_user)):
    try:
        username = user.username 
        data = await services.get_data_of_ss_threshold(username)
        return data
    except Exception as e:
        # Catch all other exceptions and log them
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    

# send current criticality checking emails of user 1
@router.get("/settings/get_current_criticality_checking_emails", response_model=List[EmailAcc])
async def get_criticalty_checking_emails(user=Depends(get_current_user)):
    try:
        username = user.username 
        addresses_string_array = await services.get_accs_to_check_criticality(username)
        data = [EmailAcc(address=email) for email in addresses_string_array]
        return data
    except Exception as e:
        # Log the exception (optional)
        print(f"An error occurred: {e}")
        
        # Raise an HTTP exception with a 500 status code and a generic error message
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving email accounts.")

# send current criticality checking emails of user 
@router.get("/settings/get_current_overdue_issues_checking_emails", response_model=List[EmailAcc])
async def get_current_overdue_issues_checking_emails(user=Depends(get_current_user)):
    try:
        username = user.username 
        addresses_string_array = await services.get_accs_to_check_overdue_issues(username)
        data = [EmailAcc(address=email) for email in addresses_string_array]
        return data
    except Exception as e:
        # Log the exception (optional)
        print(f"An error occurred: {e}")
        
        # Raise an HTTP exception with a 500 status code and a generic error message
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving email accounts.")


# send current notification channel data of user 
@router.get("/settings/get_noti_channels_data", response_model=NotiSendingChannelsRecord)
async def get_noti_channels_data(user=Depends(get_current_user)):
    try:
        username = user.username
        result = collection_notificationSendingChannels.find_one({"user_name": username})
        if result:
            formatted_result =  NotiSendingChannelsRecord(
            user_name= result['user_name'],
            is_dashboard_notifications = result['is_dashboard_notifications'],
            is_email_notifications =result['is_email_notifications'],
            noti_sending_emails = [EmailAcc(address=email) for email in result['noti_sending_emails']]
            )
            return formatted_result
        else:
            formatted_result = NotiSendingChannelsRecord(
            user_name = "",
            is_dashboard_notifications = False,
            is_email_notifications= False,
            noti_sending_emails= []
            )
            
        return formatted_result
    except Exception as e:
        # Log the exception (optional)
        print(f"An error occurred: {e}")
        
        # Raise an HTTP exception with a 500 status code and a generic error message
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving email accounts.")
    
# send system configuration data of company
@router.get("/settings/get_system_configuration_data", response_model=SendSystemConfigData)
async def get_system_configuration_data():
    try:
        result = collection_configurations.find_one({"id": 1})
        
        if result:
            formatted_result = SendSystemConfigData(overdue_margin_time= result["overdue_margin_time"])
        else:
            formatted_result = SendSystemConfigData(overdue_margin_time=14)
        
        return formatted_result
    except Exception as e:
        # Log the exception (optional)
        print(f"An error occurred: {e}")
        
        # Raise an HTTP exception with a 500 status code and a generic error message
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving email accounts.")

# send issue type and inquiry type data of company
@router.get("/settings/get_issue_inq_type_data", response_model=IssueInqTypeData)
async def get_issue_inq_type_data():
    try:
        result = collection_configurations.find_one({"id": 3})
        
        if result:
            formatted_result = IssueInqTypeData(issue_types_to_check = result['issue_types'], 
                                                inquiry_types_to_check = result['inquiry_types'])
        else:
            formatted_result = IssueInqTypeData(issue_types_to_check=[], inquiry_types_to_check=[])
        print("sent issue n inquriy type data", formatted_result)
        return formatted_result
    except Exception as e:
        # Log the exception (optional)
        print(f"An error occurred: {e}")
        
        # Raise an HTTP exception with a 500 status code and a generic error message
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving email accounts.")
    
           
@router.get("/settings/get_new_intergrating_email_id", response_model=GetNewIntergratingEmailID)
async def get_new_intergrating_email_id():
    try:
        return await services.get_new_intergrating_email_id()  
    except Exception as e:
        # Log the exception (optional)
        print(f"An error occurred: {e}")
        
        # Raise an HTTP exception with a 500 status code and a generic error message
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving email accounts.")
     
