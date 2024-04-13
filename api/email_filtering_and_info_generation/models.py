from pydantic import BaseModel
from typing import List

class Email_msg(BaseModel):
    id:str
    recipient:str
    sender:str
    subject:str
    thread_id:str
    criticality_category:str
    org_sentiment_score:int
    our_sentiment_score:int
    topics: List[str]
    
class Reading_email_acc(BaseModel):
    id:int
    address:str
    nickname:str
    
    
class Trigger_event(BaseModel):
    triggered_trig_id:int
    user_id:int
    email_msg_id:str
    recepient_email:str
    sender_email:str
    is_lower_bound_triggered:str
    is_upper_bound_triggered:str
    triggered_bound_value:str
    criticality_condition:str