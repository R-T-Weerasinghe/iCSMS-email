from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from Email.auth import gmail_auth
import base64
import email
from datetime import datetime
from Email.TypeEmail import Email

creds = gmail_auth()
# passing the arguemnts locally increase the speed. Since function will first look for the local variable and then the global variable.

def list_labels(creds=creds) -> None:
    """
    List all labels in the user's Gmail account.
    """
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        if not labels:
            print("No labels found.")
            return
        return labels

    except HttpError as error:
        raise error


def get_email_ids(*, maxResults, creds=creds) -> list | None:
    """
    List all message IDs in the user's Gmail account.
    """
    message_ids = []
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", maxResults=maxResults).execute()
        messages = results.get("messages", [])

        if not messages:
            return
        # print("Message IDs:")
        for message in messages:
            # print(message["id"])
            message_ids.append(message["id"])
        return message_ids
    
    except HttpError as error:
        raise error


def get_email_body_by_id(id, creds=creds) -> Email | None:
    """
    Get the email body by ID v1.
    """
    email: Email = dict()
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().get(userId="me", id=id).execute()
        email["emailId"] = results["id"]
        for header in results["payload"]["headers"]:
            if header["name"] == "Subject":
                email["subject"] = header["value"]
            elif header["name"] == "From":
                email["senderEmail"] = header["value"]
            elif header["name"] == "To":
                email["receiverEmail"] = header["value"]
            elif header["name"] == "Date":
                email["sentTime"] = header["value"]

        # TODO - Recheck these body parts
        if "parts" in results["payload"]:
            if results["payload"]["parts"][0]["mimeType"] == "text/plain":
                data = results["payload"]["parts"][0]["body"]["data"]
            else:
                data = results["payload"]["parts"][0]["parts"][0]["body"]["data"]
        else:
            data = results["payload"]["body"]["data"]
        data = data.replace("-", "+").replace("_", "/")
        decoded_data = base64.b64decode(data)
        email["body"] = decoded_data
        # email["Body"] = decoded_data.decode("utf-8")
        email["pulledTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return email

    except HttpError as error:
        raise error
    except KeyError as error:
        raise error

# FIXME - This function is not used currently
def getMessage(message_id, credentials=creds):
    """
    Get the email body by ID v2.
    """
    # get a message
    try:
        service = build('gmail', 'v1', credentials=credentials)

        # Call the Gmail v1 API, retrieve message data.
        message = service.users().messages().get(userId='me', id=message_id, format='raw').execute()

        # Parse the raw message.
        mime_msg = email.message_from_bytes(base64.urlsafe_b64decode(message['raw']))

        # print(mime_msg['from'])
        # print(mime_msg['to'])
        # print(mime_msg['subject'])

        # Find full message body
        message_main_type = mime_msg.get_content_maintype()
        if message_main_type == 'multipart':
            msg = ""
            for part in mime_msg.get_payload():
                if part.get_content_maintype() == 'text':
                    msg += part.get_payload() + '\n'
            return '\n'.join(msg)
        elif message_main_type == 'text':
            return mime_msg.get_payload()

        # Message snippet only.
        # print('Message snippet: %s' % message['snippet'])
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'A message get error occurred: {error}')

if __name__ == "__main__":
    print("Run main.py")