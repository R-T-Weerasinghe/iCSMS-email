import asyncio
from api.email_filtering_and_info_generation.routes import send_trig_event
from api.email_filtering_and_info_generation.routes import get_triggers_array
new_email_notification_info_array=[]



# this will later taken by the DB
# triggers_array=[{"trigger_id":1,"user_id":1,"accs_to_check_ss":["raninduharischandra12@gmail.com","ranindu2@outlook.com"], 
                # "accs_to_check_criticality":["raninduharischandra12@gmail.com"], "ss_lower_bound":-0.5, "ss_upper_bound":None},
                # {"trigger_id":2,"user_id":2,"accs_to_check_ss":["raninduharischandra12@gmail.com","ranindu2@outlook.com"], 
                #  "accs_to_check_criticality":["raninduharischandra12@gmail.com"], "ss_lower_bound":-0.8, "ss_upper_bound":0.7}]



async def identify_notifcations(new_email_msg_array):
    
    triggers_array = await get_triggers_array()
    
    
    trigger_events=[]
    
    for new_email_msg in new_email_msg_array:
        
        # checking criticality in the single new email msg
        if new_email_msg['criticality_category']=="High Criticality" or new_email_msg['criticality_category']=="Low Criticality":
            # finding the matching triggers and making a new trigger event
            for trigger in triggers_array:
                if new_email_msg["recipient"] in trigger["accs_to_check_criticality"]:
                    # making a new trigger event for a trigger match
                    new_trigger_event = {"triggered_trig_id":trigger["trigger_id"], "user_id":trigger["user_id"], "email_msg_id":new_email_msg["id"],
                                       "recepient_email":new_email_msg["recipient"], "sender_email":new_email_msg["sender"],
                                       "is_lower_bound_triggered":"no", "is_upper_bound_triggered":"no", "triggered_bound_value":None,
                                       "criticality_condition":new_email_msg['criticality_category']}
                    
                    trigger_events.append(new_trigger_event)
        
        # checking the sentiment shifts
        for trigger in triggers_array:
            
            if new_email_msg["recipient"] in trigger["accs_to_check_ss"]:
                
                #checking upper bound sentiment shift
                if trigger["ss_upper_bound"]!=None:
                    if new_email_msg["org_sentiment_score"]>trigger["ss_upper_bound"]:
                        
                        # making a new trigger event for a trigger match
                        new_trigger_event = {"event_id":2, "trig_id":trigger["trigger_id"], "user_id":trigger["user_id"], "email_msg_id":new_email_msg["id"],
                                            "recepient_email":new_email_msg["recipient"], "sender_email":new_email_msg["sender"],
                                            "is_lower_bound_triggered":"no", "is_upper_bound_triggered":"yes", "triggered_bound_value":trigger["ss_upper_bound"],
                                            "criticality_condition":null}
                        
                        trigger_events.append(new_trigger_event)
                    
                #checking lower bound sentiment shift
                if trigger["ss_lower_bound"]!=None:
                    if new_email_msg["org_sentiment_score"]<trigger["ss_lower_bound"]:
                        
                        # making a new trigger event for a trigger match
                        new_trigger_event = {"event_id":3, "trig_id":trigger["trigger_id"], "user_id":trigger["user_id"], "email_msg_id":new_email_msg["id"],
                                            "recepient_email":new_email_msg["recipient"], "sender_email":new_email_msg["sender"],
                                            "is_lower_bound_triggered":"yes", "is_upper_bound_triggered":"no", "triggered_bound_value":trigger["ss_lower_bound"],
                                            "criticality_condition":null}
                        
                        trigger_events.append(new_trigger_event)
                 
                 
    # print the whole trigger events array to check
    print("trigger_events array:")             
    print(trigger_events)
    
    await push_new_trigger_events_to_DB(trigger_events)
    
async def push_new_trigger_events_to_DB(new_trig_events_array):
    
        for new_trig_event in new_trig_events_array:
        
            await send_trig_event(new_trig_event)
    
                 
    