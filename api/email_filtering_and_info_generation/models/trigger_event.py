from pydantic import BaseModel


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
    