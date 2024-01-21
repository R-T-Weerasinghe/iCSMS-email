from gmail_API import get_email_ids, get_email_body_by_id, getMessage
import httplib2
from bs4 import BeautifulSoup as bs  # for parsing HTML
from EmailType import Email

# TODO - email are not formatted correctly. Some information can be lost thus look for a better way to parse email body
def identify_new_emails() -> list[Email]:
    """Identify new emails and return them unmasked"""
    con = httplib2.HTTPConnectionWithTimeout("127.0.0.1", 8000)
    con.request("GET", "/api/email/id")
    response = con.getresponse()

    # remove {b'} and {'}. Response.read() is in b'["123","123"]' format
    # now response is in string type. eval is used to convert it to list
    stored_ids = eval(str(response.read())[2:-1])

    # new_email_ids = []
    all_ids = get_email_ids()
    new_ids = list(set(all_ids) - set(stored_ids))

    new_emails = []
    for new_id in new_ids:
        # new_emails.append(get_email_body_by_id(new_id))
        email = get_email_body_by_id(new_id)
        if email["body"]:
            soup = bs(email["body"], features="html.parser")
            # soup.find('footer').decompose()
            email_body = soup.get_text()
            email_body = email_body.replace("\n", " ").replace("\r", " ")
            email_body = " ".join(email_body.split()) # remove extra spaces
            email["body"] = email_body
            new_emails.append(email)

    return new_emails

if __name__ == "__main__":
    print("Run main.py")
