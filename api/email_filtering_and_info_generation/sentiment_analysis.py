from api.dashboard.services import get_reading_emails_array
from external_services.aws_comprehend.sentiment_analysis import analyze_sentiment
from utils.helpers import scale_score

async def identify_sentiments(new_email_msg_array):
    
    email_acc_array = await get_reading_emails_array()
    email_acc_array = [email_acc['address'] for email_acc in email_acc_array]
    
    for new_email_msg in new_email_msg_array:
        new_email_msg["type"] = "company"
        
        for email_acc in email_acc_array:
            if email_acc in new_email_msg['recipient']:
                new_email_msg["type"] = "client"
                
        if new_email_msg["type"] == "client":

            
            new_email_msg["type"] = "client"
            sentiment_score = scale_score(analyze_sentiment(new_email_msg["body"]))
            new_email_msg["our_sentiment_score"] = sentiment_score
