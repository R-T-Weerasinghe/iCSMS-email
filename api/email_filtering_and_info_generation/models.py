from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Email_msg(BaseModel):
    id:str
    time:datetime
    recipient:str
    sender:str
    subject:str
    thread_id:str
    criticality_category:str
    org_sentiment_score:float
    our_sentiment_score:float
    products: List[str]
    isSuggestion:bool
    isIssue:bool
    isInquiry:bool
    
class Convo_summary(BaseModel):
    thread_id:str
    subject:str
    summary:str
    email_ids:List[str]
    
class Suggestion(BaseModel):
    email_id:str
    suggestion:str
    prodcuts:List[str]
    date:datetime
    recepient:str
    
class Issue(BaseModel):
    thread_id:str
    recepient_email:str
    issue_summary:str
    issue_convo_summary:str
    issue_type:str
    prodcuts:List[str]
    status:str
    start_time:datetime
    end_time: Optional[datetime] = None
    effectiveness: Optional[str] = None
    efficiency: Optional[str] = None
    isOverdue:bool
    

class Inquiry(BaseModel):
    thread_id:str
    recepient_email:str
    inquiry_summary:str
    inquiry_convo_summary:str
    inquiry_type:str
    prodcuts:List[str]
    product:str
    status:str
    start_time:datetime
    end_time: Optional[datetime] = None
    effectiveness: Optional[str] = None
    efficiency: Optional[str] = None
    isOverdue:bool
    
    
class Reading_email_acc(BaseModel):
    id:int
    address:str
    nickname:str
    
    
class Trigger_event(BaseModel):
    triggered_trig_id:int
    user_id:int
    is_lower_bound_triggered:str
    is_upper_bound_triggered:str
    triggered_bound_value:str
    
class Overdue_trig_event(BaseModel):
    triggered_trig_id:int
    user_id:int
    thread_id:str
    recepient_email:str
    


# class Trigger_event(BaseModel):
#     triggered_trig_id:int
#     user_id:int
#     email_msg_id:str
#     recepient_email:str
#     sender_email:str
#     is_lower_bound_triggered:str
#     is_upper_bound_triggered:str
#     triggered_bound_value:str
#     criticality_condition:str