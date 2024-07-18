from datetime import datetime, timedelta
import os
import time

from api.email_filtering_and_info_generation.configurations.database import collection_readingEmailAccounts, collection_inquiries,collection_issues, collection_notificationSendingChannels, collection_configurations
from api.email_filtering_and_info_generation.email_sending import send_email
from api.email_filtering_and_info_generation.models import MailObject, Maindashboard_trig_event
from api.email_filtering_and_info_generation.services import get_overall_sentiment_value, get_overdue_inquiries, get_overdue_issues, get_triggers_array, send_main_dashboard_notification_trigger_event, send_overdue_trigger_event, send_trig_event
from api.v2.dependencies import configurations


interval = 60
next_time = time.time() + interval
action_link = configurations.webapp_url + "/email/dashboard"


def get_seconds_until(target_hour, target_minute=0):
    now = datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if target_time < now:
        target_time += timedelta(days=1)
    return (target_time - now).total_seconds()


def get_all_reading_email_addresses():
    

    # Retrieve all documents from the collection
    documents = collection_readingEmailAccounts.find({}, {"address": 1, "_id": 0})  # Project only the 'address' field

    addresses = [doc["address"] for doc in documents if "address" in doc]

    return addresses

async def identify_overdue_inquiries():
    document = collection_configurations.find_one({"id":1})
    overdue_margin_time = 14
    
    if document:
        overdue_margin_time = document.get("overdue_margin_time")
        
        new_overdue_inquiries = await get_overdue_inquiries(overdue_margin_time) 
        
        for new_overdue_inquiry in new_overdue_inquiries:
            
            # update the issues collection
            result = collection_inquiries.update_one(
            {"thread_id": new_overdue_inquiry["thread_id"]},
            {"$set": {"isOverdue":True}}
            )
    else:
        collection_configurations.insert_one({"id":1, "overdue_margin_time":14, "products":[]})

async def check_sentiment_threshold_notification_condition():
    
    reading_email_addresses = get_all_reading_email_addresses()
    no_of_reading_email_addresses = len(reading_email_addresses)
    
    print("reading_email_addresses at the begining", reading_email_addresses)
    
    overall_sentiments_dict = {}
    
    overall_sentiment_scores_sum = 0
    overall_number_of_emails = 0
    
    triggers_array = await get_triggers_array()
    
    for reading_email_address in reading_email_addresses:
        
        sentiment_info_array = await get_overall_sentiment_value(reading_email_address, 20)
        print("sentiment_info_array",sentiment_info_array)
        if sentiment_info_array == 0:
            reading_email_addresses.remove(reading_email_address)
            print("reading_email_addresses after DELETION", reading_email_addresses)
        
        else:
            overall_sentiments_dict[reading_email_address] = sentiment_info_array[0]
            overall_sentiment_scores_sum = overall_sentiment_scores_sum + sentiment_info_array[1]
            overall_number_of_emails = overall_number_of_emails + sentiment_info_array[2]
    
    if overall_number_of_emails >0:
        overall_sentiments_dict["overall"] = overall_sentiment_scores_sum/overall_number_of_emails
    else:
        overall_sentiments_dict["overall"] = 0
    
    print("overall_sentiments_dict", overall_sentiments_dict,"\n")
    # checking and sending ss_threshold notification of each READING EMAIL
    for reading_email_address in reading_email_addresses:
        
        for trigger in triggers_array:
            
           
            
            if(trigger["is_checking_ss"]):
                
                print("trigger :", trigger, "\n \n")
            
                if reading_email_address in trigger["accs_to_check_ss"]:
                    
                    ss_trig_type = "none"
                
                    print("overall_sentiments_dict[reading_email_address]",overall_sentiments_dict[f"{reading_email_address}"])
                    if overall_sentiments_dict[f"{reading_email_address}"] < trigger["ss_lower_bound"]:
                        
                        trig_event = {"triggered_trig_id":trigger["trigger_id"], "user_name":trigger["user_name"],
                                    "email_msg_or_thread_id":None,"recepient_email":reading_email_address, "sender_email":None, "time":datetime.utcnow(),
                                    "is_lower_bound_triggered":'yes',  
                                    "is_upper_bound_triggered":'no', 'triggered_bound_value':overall_sentiments_dict[f"{reading_email_address}"],
                                    }
                        
                                        
                        send_trig_event(trig_event)
                        
                        print("TRIGGERED EVENT", trig_event)
                        
                        ss_trig_type = "lower"
                        
                    
                    
                    if overall_sentiments_dict[f"{reading_email_address}"]  > trigger["ss_upper_bound"]:
                        
                        trig_event = {"triggered_trig_id":trigger["trigger_id"], "user_name":trigger["user_name"], 
                                    "email_msg_or_thread_id":None,"recepient_email":reading_email_address, "sender_email":None, "time":datetime.utcnow(),
                                    "is_lower_bound_triggered":'no', 
                                    "is_upper_bound_triggered":'yes', 'triggered_bound_value':overall_sentiments_dict[f"{reading_email_address}"],
                                    }
                        
                        send_trig_event(trig_event)
                        
                        print("TRIGGERED EVENT", trig_event)
                        
                        ss_trig_type = "upper"
                    
                    if ss_trig_type != "none":
                        
                        notific_channel = collection_notificationSendingChannels.find_one({"user_name":trigger["user_name"]})
                        print("NOTIFIC CHANNEL", notific_channel)
                        if notific_channel:
                            # Access the noti_sending_emails array
                            noti_sending_emails = notific_channel.get("noti_sending_emails", [])
                            print("noti sedning EMAILS", noti_sending_emails)
                            
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
                                        Note that the above score is based upon the emails that were received within the past 29 days."""
                                    
                                    if ss_trig_type == "lower" or ss_trig_type == "upper":
                                        
                                        mail_obj = MailObject(
                                            to=noti_sending_emails,
                                            subject=subject,
                                            template_name="email_noti_template.html",
                                            context={"message": message, "action_link": action_link}
                                        )
                
                                        
                                        await send_email(mail_obj)  
                                                                   
                    
                                
                            is_dashboard_notifications = notific_channel.get("is_dashboard_notifications")
                            
                            if is_dashboard_notifications:
                                    
                                if ss_trig_type == "lower":
                                
                                    maindashboard_trig_event = Maindashboard_trig_event(
                                        triggered_trig_id = trigger['trigger_id'],
                                        user_name = trigger['user_name'],
                                        time = datetime.utcnow(),
                                        email_msg_or_thread_id = None,
                                        title= "High NEGATIVE Overall Sentiment Score Recorded",
                                        description = f"""the overall sentiment score of the {reading_email_address}, has gone below the negative sentiment
                                    threshold of {trigger["ss_lower_bound"]}. At {time.time()} on {time.month} {time.day} of the sending of this email,
                                    the overall sentiment score of the whole customer care email system was  
                                    recorded to be {overall_sentiments_dict[reading_email_address]}."""          
                                    )
                                    
                                elif ss_trig_type == "upper":
                                    
                                    maindashboard_trig_event = Maindashboard_trig_event(
                                        triggered_trig_id = trigger['trigger_id'],
                                        user_name = trigger['user_name'],
                                        time = datetime.utcnow(),
                                        email_msg_or_thread_id = None,
                                        title= "High Positive Overall Sentiment Score Recorded",
                                        description = f"""the overall sentiment score of the {reading_email_address},, has gone above the positive sentiment
                                    threshold of {trigger["ss_upper_bound"]}. At {time.time()} on {time.month} {time.day} of the sending of this email,
                                    the overall sentiment score of the whole customer care email system was  
                                    recorded to be {overall_sentiments_dict[reading_email_address]}."""
                                        
                                    )
                                    
                            await send_main_dashboard_notification_trigger_event(maindashboard_trig_event)
                                                            
                            # perform the POST call to the main dashboard
                            print("sent notification to main dashboard")                               

                            
    
    # checking and sending ss_threshold notification of the OVERALL system
    for trigger in triggers_array:
        
        reading_email_address = "overall"
        
        
        
        if(trigger["is_checking_ss"]):
            
            reading_email_address_set = set(reading_email_addresses)
            trigger_checking_email_address_set = set(trigger["accs_to_check_ss"])
            
            if reading_email_address_set.issubset(trigger_checking_email_address_set):
                
                ss_trig_type = "none"
                
                if overall_sentiments_dict["overall"] < trigger["ss_lower_bound"]:
                    
                    trig_event = {"triggered_trig_id":trigger["trigger_id"], "user_name":trigger["user_name"], 
                                "email_msg_or_thread_id":None,"recepient_email":"overall", "sender_email":None, "time":datetime.utcnow(),
                                "is_lower_bound_triggered":'yes',  
                                "is_upper_bound_triggered":'no', 'triggered_bound_value':overall_sentiments_dict[f"{reading_email_address}"],
                                }
                    
                                    
                    send_trig_event(trig_event)
                    
                    print("TRIGGER EVENT", trig_event)
                    
                    ss_trig_type = "lower"
                    
                
                
                if overall_sentiments_dict["overall"]  > trigger["ss_upper_bound"]:
                    
                    trig_event = {"triggered_trig_id":trigger["trigger_id"], "user_name":trigger["user_name"],
                                "email_msg_or_thread_id":None,"recepient_email":"overall", "sender_email":None, "time":datetime.utcnow(),
                                "is_lower_bound_triggered":'no', 
                                "is_upper_bound_triggered":'yes', 'triggered_bound_value':overall_sentiments_dict[f"{reading_email_address}"],
                                }
                    
                    send_trig_event(trig_event)
                    print("TRIGGER EVENT", trig_event)
                    
                    ss_trig_type = "upper"
                
                if ss_trig_type != "none":
                    
                    notific_channel = collection_notificationSendingChannels.find_one({"user_name":trigger["user_name"]})
                    print("NOTIFIC CHANNEL", notific_channel)
                    if notific_channel:
                        # Access the noti_sending_emails array
                        noti_sending_emails = notific_channel.get("noti_sending_emails", [])
                        
                        print("noti sedning EMAILS", noti_sending_emails)
                        
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
                                    Note that the above score is based upon the emails that were received within the past 29 days."""
                                
                                # setting up subject and message for upper threshold trigger
                                elif ss_trig_type == "upper":
                                    
                                    subject = "High Positive Overall Sentiment Score Recorded"
                                    message = f"""the overall avg sentiment score of all the email accounts , has gone above the positive sentiment
                                    threshold of {trigger["ss_upper_bound"]}. At the time of the sending of this email,
                                    the overall sentiment score of the whole customer care email system was  
                                    recorded to be {overall_sentiments_dict[reading_email_address]}.
                                    Note that the above score is based upon the emails that were received within the past 29 days."""
                                
                                if ss_trig_type == "lower" or ss_trig_type == "upper":
                                    
                                        mail_obj = MailObject(
                                            to=noti_sending_emails,
                                            subject=subject,
                                            template_name="email_noti_template.html",
                                            context={"message": message, "action_link": action_link}
                                        )
                
                                        
                                        await send_email(mail_obj)  
                                        print("emails sent")
                                                            
                
                            
                        is_dashboard_notifications = notific_channel.get("is_dashboard_notifications")
                        
                        if is_dashboard_notifications:
                            
                            if ss_trig_type == "lower":
                            
                                maindashboard_trig_event = Maindashboard_trig_event(
                                    triggered_trig_id = trigger['trigger_id'],
                                    user_name = trigger['user_name'],
                                    time = datetime.utcnow(),
                                    email_msg_or_thread_id = None,
                                    title= "High NEGATIVE Overall Sentiment Score Recorded",
                                    description = f"""the overall avg sentiment score of all the email accounts , has gone below the negative sentiment
                                threshold of {trigger["ss_lower_bound"]}. At {time.time()} on {time.month} {time.day} of the sending of this email,
                                the overall sentiment score of the whole customer care email system was  
                                recorded to be {overall_sentiments_dict[reading_email_address]}."""          
                                )
                                
                            elif ss_trig_type == "upper":
                                
                                maindashboard_trig_event = Maindashboard_trig_event(
                                    triggered_trig_id = trigger['trigger_id'],
                                    user_name = trigger['user_name'],
                                    time = datetime.utcnow(),
                                    email_msg_or_thread_id = None,
                                    title= "High Positive Overall Sentiment Score Recorded",
                                    description = f"""the overall avg sentiment score of all the email accounts , has gone above the positive sentiment
                                threshold of {trigger["ss_upper_bound"]}. At {time.time()} on {time.month} {time.day} of the sending of this email,
                                the overall sentiment score of the whole customer care email system was  
                                recorded to be {overall_sentiments_dict[reading_email_address]}."""
                                    
                                )
                                
                            await send_main_dashboard_notification_trigger_event(maindashboard_trig_event)
                                                            
                            # perform the POST call to the main dashboard
                            print("sent notification to main dashboard")
                        
    
    
    
async def check_overdue_issues():
    
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
                
                if new_overdue_issue["recepient_email"] in trigger["accs_to_check_overdue_issues"]:
                    
                    new_overdue_trig = {"triggered_trig_id":trigger['trigger_id'], "user_name":trigger['user_name'], "time":datetime.utcnow(),
                                        "thread_id":new_overdue_issue['thread_id'], "recepient_email":new_overdue_issue["recepient_email"]}
            
                    await send_overdue_trigger_event(new_overdue_trig)
                    
                    print("TRIGGER EVENT", new_overdue_trig)
                    
                    
                    # send email notification and dashboard notifications
                    
                    notific_channel = collection_notificationSendingChannels.find_one({"user_name":trigger["user_name"]})
                    
                    print("notification channel", notific_channel)
                    if notific_channel:
                        # Access the noti_sending_emails array
                        noti_sending_emails = notific_channel.get("noti_sending_emails", [])
                        
                        print("noti sedning EMAILS", noti_sending_emails)
                        
                        is_private_email_notifications = notific_channel.get("is_email_notifications")
                        
                        if is_private_email_notifications:
                        
                            if noti_sending_emails != []:
                        
                            # setting up subject and messages
                                
                                subject = f"""Overdue Issue recorded from {new_overdue_issue["recepient_email"]}"""
                                message = f"""The following issue has overdued. It has been going over for more than {overdue_margin_time} days.\n
                                Thread subject:\n
                                {new_overdue_issue["thread_subject"]}
                                The issue:\n
                                {new_overdue_issue["issue_summary"]}"""
        
                                
                                mail_obj = MailObject(
                                    to=noti_sending_emails,
                                    subject=subject,
                                    template_name="email_noti_template.html",
                                    context={"message": message, "action_link": action_link}
                                )
        
                                
                                await send_email(mail_obj)  
                                print("emails sent")
                                                             
            
                        
                        is_dashboard_notifications = notific_channel.get("is_dashboard_notifications")
                        
                        if is_dashboard_notifications:
                            
                            # perform the POST call to the main dashboard
                                maindashboard_trig_event = Maindashboard_trig_event(
                                    triggered_trig_id = trigger['trigger_id'],
                                    user_name = trigger['user_name'],
                                    time = datetime.utcnow(),
                                    email_msg_or_thread_id = new_overdue_issue['thread_id'],
                                    title= f"""Overdue Issue recorded from {new_overdue_issue["recepient_email"]}""",
                                    description = f"""The following issue has overdued. It has been going over for more than {overdue_margin_time} days.\n
                                The issue:\n
                                {new_overdue_issue["issue_summary"]}"""
                                    
                                )
                                await send_main_dashboard_notification_trigger_event(maindashboard_trig_event)
                                
                                print("sent notification to main dashboard")
                            
        
        

async def check_notifications_for_managers():
    while True:
            now = datetime.now()

            # Check if it's time to run the condition check
            if now.hour == 0 and now.minute == 0:
                await check_sentiment_threshold_notification_condition()
                await check_overdue_issues()
                await identify_overdue_inquiries()
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
            
 
        
        
        
