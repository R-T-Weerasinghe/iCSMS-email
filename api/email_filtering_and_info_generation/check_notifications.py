from datetime import datetime, timedelta
import os
import time

from simplegmail import Gmail
from api.email_filtering_and_info_generation.configurations.database import collection_email_msgs, collection_inquiries,collection_issues, collection_notificationSendingChannels, collection_configurations
from api.email_filtering_and_info_generation.routes import get_overall_sentiment_value, get_overdue_issues, get_triggers_array, send_overdue_trigger_event, send_trig_event


interval = 60
next_time = time.time() + interval


def get_seconds_until(target_hour, target_minute=0):
    now = datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if target_time < now:
        target_time += timedelta(days=1)
    return (target_time - now).total_seconds()


def get_all_reading_email_addresses():
    

    # Retrieve all documents from the collection
    documents = collection_email_msgs.find({}, {"address": 1, "_id": 0})  # Project only the 'address' field

    addresses = [doc["address"] for doc in documents if "address" in doc]

    return addresses



async def check_sentiment_threshold_notification_condition():
    
    reading_email_addresses = get_all_reading_email_addresses()
    no_of_reading_email_addresses = len(reading_email_addresses)
    
    try:
        gmail = Gmail(client_secret_file=f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{1}/client_secret.json",
                creds_file=f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{1}/gmail_token.json")

    except Exception as e:
        
        file_path =f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{1}/gmail_token.json"
        if os.path.exists(file_path):
            # Delete the file
            os.remove(file_path)
            
        time.sleep(5)
            
        gmail = Gmail(client_secret_file=f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{1}/client_secret.json",
                creds_file=f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{1}/gmail_token.json")
    
    overall_sentiments_dict = {}
    
    overall_sentiment_scores_sum = 0
    
    triggers_array = await get_triggers_array()
    
    for reading_email_address in reading_email_addresses:
        
        overall_sentiments_dict[reading_email_address] = await get_overall_sentiment_value(reading_email_address, 14)
        overall_sentiment_scores_sum = overall_sentiment_scores_sum + overall_sentiments_dict[reading_email_address]
    
    overall_sentiments_dict["overall"] = overall_sentiment_scores_sum/no_of_reading_email_addresses
       
    # checking and sending ss_threshold notification of each READING EMAIL
    for reading_email_address in reading_email_addresses:
        
        for trigger in triggers_array:
            
            if(trigger["is_checking_ss"]):
            
                if reading_email_address in trigger["accs_to_check_ss"]:
                    
                    ss_trig_type = "none"
                    
                    if overall_sentiments_dict[f"{reading_email_address}"] < trigger["ss_lower_bound"][f"{reading_email_address}"]:
                        
                        trig_event = {"triggered_trig_id":trigger["trigger_id"], "user_id":trigger["user_id"], "is_lower_bound_triggered":'yes',  
                                    "is_upper_bound_triggered":'no', 'triggered_bound_value':overall_sentiments_dict[f"{reading_email_address}"],
                                    "recepient email": reading_email_address}
                        
                                        
                        send_trig_event(trig_event)
                        
                        ss_trig_type = "lower"
                        
                    
                    
                    if overall_sentiments_dict[f"{reading_email_address}"]  > trigger["ss_upper_bound"][f"{reading_email_address}"]:
                        
                        trig_event = {"triggered_trig_id":trigger["trigger_id"], "user_id":trigger["user_id"], "is_lower_bound_triggered":'no', 
                                    "is_upper_bound_triggered":'yes', 'triggered_bound_value':overall_sentiments_dict[f"{reading_email_address}"],
                                    "recepient email": reading_email_address}
                        
                        send_trig_event(trig_event)
                        
                        ss_trig_type = "upper"
                    
                    if ss_trig_type != "none":
                        
                        notific_channel = collection_notificationSendingChannels.find({"user_id":trigger["user_id"]})
                        
                        if notific_channel:
                            # Access the noti_sending_emails array
                            noti_sending_emails = notific_channel.get("noti_sending_emails", [])
                            
                            is_private_email_notifications = notific_channel.get("is_email_notifications")
                            
                            if is_private_email_notifications:
                            
                            if noti_sending_emails != []:
                            
                                # setting up subject and message for lower threshold trigger
                                if ss_trig_type == "lower":
                                    
                                    subject = "High NEGATIVE Overall Sentiment Score Recorded"
                                    message = f"""the overall sentiment score of the {reading_email_address}, has gone below the negative sentiment
                                    threshold of {trigger["ss_lower_bound"]}. 
                                    At the time of the sending of this email,
                                    the overall sentiment score of the above mentioned email account was 
                                    recorded to be {overall_sentiments_dict[reading_email_address]}. 
                                    Note that the above score is based upon the emails that were received within the past 14 days."""
                                
                                # setting up subject and message for upper threshold trigger
                                elif ss_trig_type == "upper":
                                    
                                    subject = "High Positive Overall Sentiment Score Recorded"
                                    message = f"""the overall sentiment score of the {reading_email_address}, has gone above the positive sentiment
                                    threshold of {trigger["ss_upper_bound"]}. At the time of the sending of this email,
                                    the overall sentiment score of the above mentioned email account was 
                                    recorded to be {overall_sentiments_dict[reading_email_address]}.
                                    Note that the above score is based upon the emails that were received within the past 14 days."""
                                
                                if ss_trig_type == "lower" or ss_trig_type == "upper":
                                    
                                    for noti_sending_email in noti_sending_emails:
                                            
                                        params = {
                                        "to": noti_sending_email,
                                        "sender": "raninduharischandra12@gmail.com",
                                        "subject": subject,
                                        "msg_plain": message,
                                        "signature": True  # use my account signature
                                        }
                                        
                                        message = gmail.send_message(**params)                           
                
                            
                            is_dashboard_notifications = notific_channel.get("is_dashboard_notifications")
                            
                            if is_dashboard_notifications:
                                
                                # perform the POST call to the main dashboard
                                
                                print("sending notification to main dashboard")
                            
    
    # checking and sending ss_threshold notification of the OVERALL system
    for trigger in triggers_array:
        
        if(trigger["is_checking_ss"]):
            
            if "overall" in trigger["accs_to_check_ss"]:
                
                ss_trig_type = "none"
                
                if overall_sentiments_dict["overall"] < trigger["ss_lower_bound"][f"{reading_email_address}"]:
                    
                    trig_event = {"triggered_trig_id":trigger["trigger_id"], "user_id":trigger["user_id"], "is_lower_bound_triggered":'yes',  
                                  "is_upper_bound_triggered":'no', 'triggered_bound_value':overall_sentiments_dict[f"{reading_email_address}"],
                                  "recepient email": "overall"}
                    
                                     
                    send_trig_event(trig_event)
                    
                    ss_trig_type = "lower"
                    
                   
                
                if overall_sentiments_dict["overall"]  > trigger["ss_upper_bound"][f"{reading_email_address}"]:
                    
                    trig_event = {"triggered_trig_id":trigger["trigger_id"], "user_id":trigger["user_id"], "is_lower_bound_triggered":'no', 
                                  "is_upper_bound_triggered":'yes', 'triggered_bound_value':overall_sentiments_dict[f"{reading_email_address}"],
                                  "recepient email": "overall"}
                    
                    send_trig_event(trig_event)
                    
                    ss_trig_type = "upper"
                
                if ss_trig_type != "none":
                    
                    notific_channel = collection_notificationSendingChannels.find({"user_id":trigger["user_id"]})
                    
                    if notific_channel:
                        # Access the noti_sending_emails array
                        noti_sending_emails = notific_channel.get("noti_sending_emails", [])
                        
                        is_private_email_notifications = notific_channel.get("is_email_notifications")
                        
                        if is_private_email_notifications:
                        
                         if noti_sending_emails != []:
                        
                            # setting up subject and message for lower threshold trigger
                            if ss_trig_type == "lower":
                                
                                subject = "High NEGATIVE Overall Sentiment Score Recorded"
                                message = f"""the overall avg sentiment score of all the email accounts , has gone below the negative sentiment
                                threshold of {trigger["ss_lower_bound"]}. 
                                At the time of the sending of this email,
                                the overall sentiment score of the whole customer care email system was 
                                recorded to be {overall_sentiments_dict[reading_email_address]}. 
                                Note that the above score is based upon the emails that were received within the past 14 days."""
                            
                            # setting up subject and message for upper threshold trigger
                            elif ss_trig_type == "upper":
                                
                                subject = "High Positive Overall Sentiment Score Recorded"
                                message = f"""the overall avg sentiment score of all the email accounts , has gone above the positive sentiment
                                threshold of {trigger["ss_upper_bound"]}. At the time of the sending of this email,
                                the overall sentiment score of the whole customer care email system was  
                                recorded to be {overall_sentiments_dict[reading_email_address]}.
                                Note that the above score is based upon the emails that were received within the past 14 days."""
                            
                            if ss_trig_type == "lower" or ss_trig_type == "upper":
                                
                                for noti_sending_email in noti_sending_emails:
                                        
                                    params = {
                                    "to": noti_sending_email,
                                    "sender": "raninduharischandra12@gmail.com",
                                    "subject": subject,
                                    "msg_plain": message,
                                    "signature": True  # use my account signature
                                    }
                                    
                                    message = gmail.send_message(**params)                           
            
                        
                        is_dashboard_notifications = notific_channel.get("is_dashboard_notifications")
                        
                        if is_dashboard_notifications:
                            
                            # perform the POST call to the main dashboard
                            
                             print("sending notification to main dashboard")
                        
    
    
    
async def check_overdue_emails():
    
    document = collection_configurations.find_one({"id":1})
    overdue_margin_time = 14
    
    if document:
        overdue_margin_time = document.get("overdue_margin_time")
        
    new_overdue_issues = await get_overdue_issues(overdue_margin_time) 
    
    triggers_array = await get_triggers_array()
    
    for new_overdue_issue in new_overdue_issues:
        
        # update the issues collection
        result = collection_issues.update_one(
        {"thread_id": new_overdue_issue["thread_id"]},
        {"$set": {"isOverdue":True}}
        )
        
        for trigger in triggers_array:
            
            if new_overdue_issue["recepient_email"] in trigger["accs_to_check_overdue_emails"]:
                
                new_overdue_trig = {"triggered_trig_id":trigger['triggered_trig_id'], "user_id":trigger['user_id'],
                                    "thread_id":new_overdue_issue['thread_id'], "recepient_email":new_overdue_issue["recepient_email"]}
        
                await send_overdue_trigger_event(new_overdue_trig)
        

async def check_notifications_for_managers():
    while True:
            now = datetime.now()

            # Check if it's time to run the condition check
            if now.hour == 0 and now.minute == 0:
                await check_sentiment_threshold_notification_condition()
                await check_overdue_emails()
                time.sleep(60)  # Sleep for 1 minute to avoid multiple checks within the same minute

            elif now.hour == 12 and now.minute == 0:
                await check_sentiment_threshold_notification_condition()
                time.sleep(60)  # Sleep for 1 minute to avoid multiple checks within the same minute

            # Calculate time to sleep until the next check (either 00:00 or 12:00)
            seconds_until_midnight = get_seconds_until(0)
            seconds_until_noon = get_seconds_until(12)

            # Sleep until the next scheduled check time
            sleep_time = min(seconds_until_midnight, seconds_until_noon)
            time.sleep(sleep_time)
        
        
        
