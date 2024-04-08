from pydantic import BaseModel


class Email_msg(BaseModel):
    id:str
    recipient:str
    sender:str
    subject:str
    thread_id:str
    criticality_category:str
    org_sentiment_score:int
    our_sentiment_score:int