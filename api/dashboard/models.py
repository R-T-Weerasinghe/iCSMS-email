
    
from pydantic import BaseModel


class get_current_overall_sentiments_response(BaseModel):
    positive_percentage:float
    neutral_percentage:float
    negative_percentage:float
