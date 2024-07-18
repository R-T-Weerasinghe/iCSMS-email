from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Email_msg(BaseModel):
    id:str
    time:datetime
    recipient:str
    sender:str
    subject:str
    type: str
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
    updated_times:List[datetime]
    summary:str
    products:List[str]
    
class Suggestion(BaseModel):
    email_id:str
    suggestion:str
    prodcuts:List[str]
    date:datetime
    recepient:str
    
class IssueInDB(BaseModel):
    thread_id:str
    thread_subject:str
    recepient_email:str
    sender_email: str
    issue_summary:str
    issue_convo_summary_arr:List[dict]
    status:str
    ongoing_status:Optional[str] = None
    issue_type:str
    products:List[str] = []
    sentiment_score: float
    start_time:datetime
    updated_time:datetime
    end_time: Optional[datetime] = None
    effectiveness: Optional[str] = None
    efficiency: Optional[str] = None
    isOverdue:bool
    

class InquiryInDB(BaseModel):
    thread_id:str
    thread_subject: str
    recepient_email:str
    sender_email: str
    inquiry_summary:str
    inquiry_convo_summary_arr:List[dict]
    status:str
    ongoing_status:Optional[str] = None
    inquiry_type:str
    products:List[str] = []
    sentiment_score: float
    start_time:datetime
    updated_time:datetime
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
    user_name:str
    email_msg_or_thread_id:Optional[str] = None
    recepient_email: Optional[str] = None
    sender_email: Optional[str] = None
    time:datetime
    is_lower_bound_triggered:str
    is_upper_bound_triggered:str
    triggered_bound_value:str
    criticality_condition:str
    
class Overdue_trig_event(BaseModel):
    triggered_trig_id:int
    user_name:str
    time: datetime
    thread_id:str
    recepient_email:str

class Maindashboard_trig_event(BaseModel):
    triggered_trig_id:int
    user_name:str
    time: datetime
    email_msg_or_thread_id:Optional[str] = None
    title:str
    description:str
    
class MailObject(BaseModel):
    to: list[str]
    subject: str
    context: dict  # a dictionary containing placeholders and their values to replace in html template 
    template: str  # html template file name (without .html part)
    


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