from pydantic import BaseModel
from typing import List


# Define a Pydantic model for the data sent from Angular
class IntergratingEmailData(BaseModel):
        emailAddress: str
        nickName: str
        clientSecret:str

class Trigger(BaseModel):
     trigger_id:int
     user_id:int
     accs_to_check_ss:List[str]
     accs_to_check_criticality:List[str]
     ss_lower_bound:int
     ss_upper_bound:int

class NotiSendingChannelsRecord(BaseModel):
        user_id:int
        is_dashboard_notifications: bool
        is_email_notifications: bool
        noti_sending_emails:List[str]