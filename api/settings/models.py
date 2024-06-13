from pydantic import BaseModel
from typing import List


# Define a Pydantic model for the data sent from Angular

class  EmailAcc(BaseModel):
    address: str

class EmailAccWithNickName(BaseModel):
    address:str
    nickname:str
    
class IntergratingEmailData(BaseModel):
        emailAddress: str
        nickName: str
        clientSecret:str

class Trigger(BaseModel):
     trigger_id:int
     user_name:str
     is_checking_ss:bool
     accs_to_check_ss:List[str]
     accs_to_check_overdue_issues:List[str]
     accs_to_check_critical_emails:List[str]
     ss_lower_bound:int
     ss_upper_bound:int
     is_lower_checking:bool
     is_upper_checking:bool

class NotiSendingChannelsRecord(BaseModel):
        user_name:str
        is_dashboard_notifications: bool
        is_email_notifications: bool
        noti_sending_emails:List[EmailAcc]
        

    
class  SendSystemConfigData(BaseModel):
    overdue_margin_time: int
    

    
class  SSShiftData(BaseModel):
        accs_to_check_ss = List[EmailAcc]
        ss_lower_bound = float
        ss_upper_bound = float
        is_checking_ss = bool
        is_lower_checking = bool
        is_upper_checking = bool
        
class UserRoleResponse(BaseModel):
        isAdmin:bool
        
class DeleteNotiSendingEmail:
  noti_sending_emails: List[str]
  
class DeleteReadingEmail:
  removing_email: str
  
class PostNewIntegratingEmail:
  emailAddress: str
  nickName: str
  clientSecret:str

class PostingNotiSendingChannelsRecord:
  is_dashboard_notifications: bool
  is_email_notifications: bool
  noti_sending_emails:List[str]
  
class PostingCriticalityData:
  accs_to_check_criticality: List[str]
  
  
class PostingOverdueIssuesData:
  accs_to_check_overdue_emails: List[str]