from gmail_API import get_message_ids
import httplib2


def identify_new_emails():
    """Identify new email IDs"""
    con = httplib2.HTTPConnectionWithTimeout("127.0.0.1", 8000)
    con.request("GET", "/api/email/id")
    response = con.getresponse()

    # remove {b'} and {'}. Response.read() is in b'["123","123"]' format
    # now response is in string type. eval is used to convert it to list
    stored_ids = eval(str(response.read())[2:-1]) 

    # new_email_ids = []
    all_email_ids = get_message_ids()
    print(all_email_ids)
    # # if email IDs are not found, return
    # if not all_email_ids:
    #     return None
    # # if head_email_id is not set, set it to the first email ID
    # if not head_email_id:
    #     head_email_id = all_email_ids[0]

    # while head_email_id not in all_email_ids:
    #     new_email_ids.append(get_email_ids())

    # if new_email_ids:
    #     head_email_id = new_email_ids[0]
    # else:
    #     print("No messages found or id error.")




identify_new_emails()
