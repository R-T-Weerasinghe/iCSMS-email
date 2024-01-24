from Email.gmail_API import get_email_ids, get_email_body_by_id, getMessage
import httplib2
from bs4 import BeautifulSoup as bs  # for parsing HTML
from Email.TypeEmail import Email
from Email.parse_html import html_to_text

# TODO - email are not formatted correctly. Some information can be lost thus look for a better way to parse email body
def identify_new_emails(*, return_raw=False) -> list[Email]:
    """
    Identify new emails and return them unmasked

    Args:
      return_raw: return raw email body (i.e. in HTML format)
    """
    con = httplib2.HTTPConnectionWithTimeout("127.0.0.1", 8000)
    con.request("GET", "/api/email/id")
    response = con.getresponse()

    # remove {b'} and {'}. Response.read() is in b'["123","123"]' format
    # now response is in string type. eval is used to convert it to list
    stored_ids = eval(str(response.read())[2:-1])

    # new_email_ids = []
    all_ids = get_email_ids(maxResults=1)
    new_ids = list(set(all_ids) - set(stored_ids))

    new_emails = []
    for new_id in new_ids:
        email = get_email_body_by_id(new_id)
        if return_raw:
            new_emails.append(email)
        else:
            if email["body"]:   # Null check
                email["body"] = html_to_text(email["body"])
                new_emails.append(email)
            else:
                raise Exception("Email body is null")
            
    return new_emails

if __name__ == "__main__":
    print("Run main.py")
