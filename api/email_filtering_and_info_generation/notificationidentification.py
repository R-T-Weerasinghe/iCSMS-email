import asyncio
from datetime import datetime
from api.email_filtering_and_info_generation.email_sending import send_email
from api.email_filtering_and_info_generation.models import MailObject, Maindashboard_trig_event
from api.email_filtering_and_info_generation.services import send_main_dashboard_notification_trigger_event, send_trig_event
from api.email_filtering_and_info_generation.services import get_triggers_array
from api.email_filtering_and_info_generation.configurations.database import collection_notificationSendingChannels
from api.v2.dependencies import configurations
new_email_notification_info_array=[]
action_link = configurations.webapp_url + "/email/dashboard"

async def identify_criticality_notifcations(new_email_msg_array):
    
    triggers_array = await get_triggers_array()
    
    
    trigger_events=[]
    
    for new_email_msg in new_email_msg_array:
        
        # checking criticality in the single new email msg
        if new_email_msg['criticality_category']=="High Criticality" or new_email_msg['criticality_category']=="Medium Criticality":
            # finding the matching triggers and making a new trigger event
            for trigger in triggers_array:
                if new_email_msg["recipient"] in trigger["accs_to_check_criticality"]:
                    # making a new trigger event for a trigger match
                    new_trigger_event = {"triggered_trig_id":trigger["trigger_id"], "user_name":trigger["user_name"], "email_msg_or_thread_id":new_email_msg["id"],
                                       "recepient_email":new_email_msg["recipient"], "sender_email":new_email_msg["sender"], "time":new_email_msg["time"],
                                       "is_lower_bound_triggered":"no", "is_upper_bound_triggered":"no", "triggered_bound_value":None,
                                       "criticality_condition":new_email_msg['criticality_category']}
                    
                    trigger_events.append(new_trigger_event)
                    
                    
                # SEND email notification and dashboard notifications
                
                    notific_channel = collection_notificationSendingChannels.find_one({"user_name":trigger["user_name"]})
                        
                    if notific_channel:
                        # Access the noti_sending_emails array
                        noti_sending_emails = notific_channel.get("noti_sending_emails", [])
                        
                        is_private_email_notifications = notific_channel.get("is_email_notifications")
                        
                        if is_private_email_notifications:
                        
                            if noti_sending_emails != []:
                        
                            # setting up subject and messages
                                
                                subject = f"""Criticality Email recorded from {new_email_msg["recipient"]}"""
                                message = f"""The following critical email was recorded from the account  {new_email_msg["recipient"]} on {new_email_msg["time"]}. \n\n
                                Criticality Category: {new_email_msg['criticality_category']} \n
                                sender: {new_email_msg["sender"]}\n
                                subject of email: {new_email_msg["subject"]}\n\n
                                {new_email_msg['body']}"""
                                
                                mail_obj = MailObject(
                                    to=noti_sending_emails,
                                    subject=subject,
                                    template_name="email_noti_template.html",
                                    context={"message": message, "action_link": action_link}
                                )
        
                                
                                await send_email(mail_obj)                          
            
                        
                        is_dashboard_notifications = notific_channel.get("is_dashboard_notifications")
                        
                        if is_dashboard_notifications:
                            # perform the POST call to the main dashboard
                                maindashboard_trig_event = Maindashboard_trig_event(
                                    triggered_trig_id = trigger['trigger_id'],
                                    user_name = trigger['user_name'],
                                    time = datetime.utcnow(),
                                    email_msg_or_thread_id = new_email_msg['thread_id'],
                                    title= f"""Criticality Email recorded from {new_email_msg["recipient"]}""",
                                    description = f"""The following critical email was recorded from the account  {new_email_msg["recipient"]} on {new_email_msg["time"]}. \n\n
                                Criticality Category: {new_email_msg['criticality_category']} \n
                                sender: {new_email_msg["sender"]}\n
                                subject of email: {new_email_msg["subject"]}\n\n
                                {new_email_msg['body']}"""
                                )
                                await send_main_dashboard_notification_trigger_event(maindashboard_trig_event)
                                
                                # perform the POST call to the main dashboard                           
                                print("sending notification to main dashboard")
                        
        
        # checking the sentiment shifts
        # for trigger in triggers_array:
            
        #     if new_email_msg["recipient"] in trigger["accs_to_check_ss"]:
                
        #         #checking upper bound sentiment shift
        #         if trigger["ss_upper_bound"]!=None:
        #             if new_email_msg["org_sentiment_score"]>trigger["ss_upper_bound"]:
                        
        #                 # making a new trigger event for a trigger match
        #                 new_trigger_event = {"event_id":2, "trig_id":trigger["trigger_id"], "user_name":trigger["user_name"], "email_msg_id":new_email_msg["id"],
        #                                     "recepient_email":new_email_msg["recipient"], "sender_email":new_email_msg["sender"],
        #                                     "is_lower_bound_triggered":"no", "is_upper_bound_triggered":"yes", "triggered_bound_value":trigger["ss_upper_bound"],
        #                                     "criticality_condition":null}
                        
        #                 trigger_events.append(new_trigger_event)
                    
        #         #checking lower bound sentiment shift
        #         if trigger["ss_lower_bound"]!=None:
        #             if new_email_msg["org_sentiment_score"]<trigger["ss_lower_bound"]:
                        
        #                 # making a new trigger event for a trigger match
        #                 new_trigger_event = {"event_id":3, "trig_id":trigger["trigger_id"], "user_name":trigger["user_name"], "email_msg_id":new_email_msg["id"],
        #                                     "recepient_email":new_email_msg["recipient"], "sender_email":new_email_msg["sender"],
        #                                     "is_lower_bound_triggered":"yes", "is_upper_bound_triggered":"no", "triggered_bound_value":trigger["ss_lower_bound"],
        #                                     "criticality_condition":null}
                        
        #                 trigger_events.append(new_trigger_event)
                 
                 
    # print the whole trigger events array to check
    print("trigger_events array:")             
    print(trigger_events)
    
    await push_new_trigger_events_to_DB(trigger_events)
    
async def push_new_trigger_events_to_DB(new_trig_events_array):
    
        for new_trig_event in new_trig_events_array:
        
            await send_trig_event(new_trig_event)
    
                 
    