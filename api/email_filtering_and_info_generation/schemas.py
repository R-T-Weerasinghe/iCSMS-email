def individual_email_msg_serial(email_msg) -> dict:
    return{
        "_id": str(email_msg["_id"]),#_id is format which MongoDB uses to find a key to return the value
        "id":email_msg["id"],
        "recipient": email_msg["recipient"],
        "sender": email_msg["sender"],
        "thread_id": email_msg["thread_id"],
        "criticality_category": email_msg["criticality_category"],
        "org_sentiment_score": email_msg["org_sentiment_score"],
        "our_sentiment_score": email_msg["our_sentiment_score"]

        
        
        
    }
    
def list_email_msg_serial(email_msgs) -> list:
    return[individual_email_msg_serial(email_msg) for email_msg in email_msgs]

def individual_suggestions_serial(suggestion) -> dict:
    return{
        "email_id":suggestion["email_id"],
        "suggestion": suggestion["suggestion"],        
    }
    
def list_suggestion_serial(suggestions) -> list:
    return[individual_suggestions_serial(suggestion) for suggestion in suggestions]


def individual_trigger_serial(trigr) -> dict:
    return{
        "_id": str(trigr["_id"]),#_id is format which MongoDB uses to find a key to return the value
        "trigger_id":trigr["trigger_id"],
        "user_name":trigr["user_name"],
        "accs_to_check_ss":trigr["accs_to_check_ss"],
        "accs_to_check_criticality":trigr["accs_to_check_critical_emails"],
        "ss_lower_bound":trigr["ss_lower_bound"],
        "ss_upper_bound":trigr["ss_upper_bound"]
        
    }
    
def list_trigger_serial(trigrs) -> list:
    return[individual_trigger_serial(trigr) for trigr in trigrs]



def individual_readingEmailAcc_serial(readingEmailAcc) -> dict:
    return{

        "id":readingEmailAcc["id"],
        "address": readingEmailAcc["address"],
        "nickname": readingEmailAcc["nickname"]
        
    }

def list_readingEmailAcc_serial(readingEmailAccs) -> list:
    return[individual_readingEmailAcc_serial(readingEmailAcc) for readingEmailAcc in readingEmailAccs]


        
