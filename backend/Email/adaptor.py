from gmail_API import list_labels, get_message_ids, get_email_body_by_id
from datetime import datetime

def get_recent_message_id():
    ids = get_message_ids()

    if not ids:
        raise Exception("No messages found or id error.")
    else:
        head = ids[0]
        print(datetime.now(), head, sep=" -- ")

def get_email_ids() -> list | None:
    ids = get_message_ids()
    if not ids:
        print("No messages found or id error.")
    else:
        return ids
    
get_email_body_by_id("18ce87545cc00375")


# TODO(developer): setup pubsub topic and subscription

# TODO(developer): add functions to get email IDs from pubsub subscription
# TODO(developer): add a periodic sync to prevent missed notifications from pubsub 
# TODO(tester): send emails and test 
    
