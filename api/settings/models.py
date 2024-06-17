from pydantic import BaseModel
from typing import List, Union


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
     ss_lower_bound:Union[float, None]
     ss_upper_bound:Union[float, None]
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
        accs_to_check_ss : List[EmailAcc]
        ss_lower_bound : Union[float, None]
        ss_upper_bound : Union[float, None]
        is_checking_ss : bool
        is_lower_checking : bool
        is_upper_checking : bool
        
class EditingEmailData(BaseModel):
  emailAddress: str
  nickName: str
  clientSecret:str
        
class UserRoleResponse(BaseModel):
        isAdmin:bool
        
class DeleteNotiSendingEmail(BaseModel):
  noti_sending_emails: List[str]
  
class DeleteReadingEmail(BaseModel):
  removing_email: str
  
class PostNewIntegratingEmail(BaseModel):
  emailID: int
  emailAddress: str
  nickName: str
  clientSecret:str

class GetNewIntergratingEmailID(BaseModel):
  emailID: int
  
class  PostEditingEmail(BaseModel):
  oldEmailAddress: str
  editedEmailAddress: str
  nickName: str
  clientSecret:str
  
class EmailINtegrationPostResponseMessage(BaseModel):
  message: str


class PostingNotiSendingChannelsRecord(BaseModel):
  is_dashboard_notifications: bool
  is_email_notifications: bool
  noti_sending_emails:List[str]
  
class PostingCriticalityData(BaseModel):
  accs_to_check_criticality: List[str]
  
  
class PostingOverdueIssuesData(BaseModel):
  accs_to_check_overdue_emails: List[str]