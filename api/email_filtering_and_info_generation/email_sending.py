
from email.mime.text import MIMEText
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from api.email_authorization.services import update_authorization_uri
from google_auth_oauthlib.flow import Flow # type: ignore
from pathlib import Path

from googleapiclient.discovery import build 
from google.oauth2.credentials import Credentials
import os.path 
import base64 
from bs4 import BeautifulSoup 
from datetime import datetime, timedelta, timezone
import json
import os
import time
import requests

import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from smtplib import SMTP_SSL

from jinja2 import Environment, FileSystemLoader

from api.v2.dependencies import configurations as Configurations
from api.email_filtering_and_info_generation.models import MailObject 


state_store = {}

def refresh_token(token_path):
    # Load the token data from the JSON file
    with open(token_path, 'r') as token_file:
        token_data = json.load(token_file)

    # Refresh token request parameters
    refresh_token = token_data['refresh_token']
    client_id = token_data['client_id']
    client_secret = token_data['client_secret']
    token_uri = token_data['token_uri']

    # Define the request payload
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }

    # Make the request to refresh the token
    response = requests.post(token_uri, data=payload)

    if response.status_code == 200:
        new_token_data = response.json()
        # Update the token data with the new token information
        token_data['token'] = new_token_data['access_token']
        # Update the expiry time (typically expires_in is in seconds)
        expiry_time = datetime.utcnow() + timedelta(seconds=new_token_data['expires_in'])
        token_data['expiry'] = expiry_time.isoformat() + 'Z'  # Adding 'Z' to indicate UTC

        # Save the updated token data back to the JSON file
        with open(token_path, 'w') as token_file:
            json.dump(token_data, token_file, indent=4)

        print("Token refreshed successfully!")
    else:
        print(f"Failed to refresh token: {response.status_code}")
        print(response.json())



def is_token_valid(token_file):
    try:
        with open(token_file, 'r') as file:
            token_data = json.load(file)
        
        expiration_timestamp = token_data['expiry'].rstrip('Z')
        expiration_datetime = datetime.fromisoformat(expiration_timestamp).replace(tzinfo=timezone.utc)
        current_datetime = datetime.now(timezone.utc)

        if current_datetime < expiration_datetime - timedelta(minutes=3):
            print("Token is still valid.")
            return True
        else:
            print("Token has expired.")
            if os.path.exists(token_file):
                # Delete the token file
                os.remove(token_file)    
            return False
    except FileNotFoundError:
        print("Token file not found.")
        return False
    except KeyError:
        print("Invalid token file format.")
        return False

# Initialize the OAuth flow
def init_oauth_flow(client_secrets_file: str, redirect_uri: str):
    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.modify'
        ],

        redirect_uri=redirect_uri
    )
    flow.access_type = 'offline'
    return flow


async def login_async(id: int, email_acc_address:str):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    client_secrets_file = f'api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{id}/client_secret.json'
    redirect_uri = f'http://127.0.0.1:8000/email/info_and_retrieval/callbackSending?id={id}'
    flow = init_oauth_flow(client_secrets_file, redirect_uri)

    state = os.urandom(16).hex()  # Generate a random state
    state_store[state] = id  # Store the state with the associated id

    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=state
    )
    print("authorization_url: ",authorization_url)
    await update_authorization_uri(authorization_url, email_acc_address)



# async def send_email(id: int, recepient: str, subject: str, email_body: str, ):
    
#     token_path = f'api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{id}/gmail_token.json'
    
#     if (os.path.exists(token_path)):
#         refresh_token(token_path)
    
#     if not is_token_valid(token_path):
        
#         await login_async(id, "raninduharischandra12@gmail.com")
        
    
#     while(not os.path.exists(token_path)):
#         print("inside waiting loop")
#         time.sleep(5)
    
#     print("outside of waiting loop")
#     creds = None

    
#     SCOPES = [
#     'https://www.googleapis.com/auth/gmail.readonly',
#     'https://www.googleapis.com/auth/gmail.send',
#     'https://www.googleapis.com/auth/gmail.compose',
#     'https://www.googleapis.com/auth/gmail.modify'
#     ]
    
    
    
#     creds = Credentials.from_authorized_user_file(f'api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{id}/gmail_token.json', SCOPES)


#     # Connect to the Gmail API 
#     service = build('gmail', 'v1', credentials=creds) 
#     message = MIMEText(email_body)
#     message['to'] = recepient
#     message['from'] = 'raninduharischandra12@gmail.com'
#     message['subject'] = subject
#     message_body = {
#     'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()
#     }
#     message = service.users().messages().send(userId='me', body=message_body).execute()
#     print('Message Id: %s' % message['id'])




action_link = Configurations.webapp_url + "/email/dashboard"

async def send_email(mail_obj: MailObject):
    try:
        message = MIMEMultipart()
        message["From"] = formataddr(("SentiView", Configurations.mail_username))
        message["To"] = ", ".join(mail_obj.to)
        message["Subject"] = mail_obj.subject
        
        current_file_dir = os.path.dirname(__file__)
        template_dir = os.path.join(current_file_dir, 'templates')
        

        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(mail_obj.template)

        # Render the template with the provided context
        html_content = template.render(mail_obj.context)

        # Attach the HTML content
        message.attach(MIMEText(html_content, "html"))

        with SMTP_SSL(Configurations.mail_host, Configurations.mail_port) as server:
            server.login(Configurations.mail_username, Configurations.mail_password)
            logging.info("Sending the email.")
            server.send_message(message)
            server.quit()
            logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")