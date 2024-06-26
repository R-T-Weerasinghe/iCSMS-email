from external_services.aws_comprehend.sentiment_analysis import analyze_sentiment
from utils.helpers import scale_score

async def identify_sentiments(new_email_msg_array):
    
    for new_email_msg in new_email_msg_array:
        
        sentiment_score = scale_score(analyze_sentiment(new_email_msg["body"]))
        new_email_msg["our_sentiment_score"] = sentiment_score