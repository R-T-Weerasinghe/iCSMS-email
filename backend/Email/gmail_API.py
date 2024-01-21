from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import gmail_auth
import base64
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
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


def get_message_ids(creds=creds) -> list | None:
    """
    List all message IDs in the user's Gmail account.
    """
    message_ids = []
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", maxResults=500).execute()
        messages = results.get("messages", [])

        if not messages:
            return
        # print("Message IDs:")
        for message in messages:
            # print(message["id"])
            message_ids.append(message["id"])
        return message_ids
    
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

def get_email_body_by_id(id, creds=creds):
    """
    Get the email body by ID.
    """
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().get(userId="me", id=id).execute()
        for header in results["payload"]["headers"]:
            if header["name"] == "Subject":
                subject = header["value"]
            if header["name"] == "From":
                sender = header["value"]
        data = results["payload"]["parts"][0]["body"]["data"]
        data = data.replace("-", "+").replace("_", "/")
        decoded_data = base64.b64decode(data)

        # Now, the data obtained is in lxml. So, we will parse  
        # it with BeautifulSoup library 
        print(decoded_data)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")
    except KeyError as error:
        print(f"Email message format not supported: key error {error}")

if __name__ == "__main__":
    print("Not runnable")