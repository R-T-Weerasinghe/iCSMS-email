import copy
import os
import asyncio
import json
import re

from simplegmail import Gmail # type: ignore
from simplegmail.query import construct_query # type: ignore
from datetime import datetime, timedelta, timezone
from api.email_filtering_and_info_generation.conversations_summarizing import summarize_conversations
from api.email_filtering_and_info_generation.emailIntegration import integrateEmail
from api.email_filtering_and_info_generation.criticality_identification import identify_criticality
from api.email_filtering_and_info_generation.format_email_bodies import format_email_bodies
from api.email_filtering_and_info_generation.issues_identification import identify_issues_inquiries_and_checking_status
from api.email_filtering_and_info_generation.notificationidentification import identify_notifcations
from api.email_filtering_and_info_generation.data_masking import mask_email_messages
from api.email_filtering_and_info_generation.sentiment_analysis import identify_sentiments
from api.email_filtering_and_info_generation.topic_identification import identify_topics
from api.email_filtering_and_info_generation.suggestions_identification import identify_and_summarize_suggestions


from api.email_authorization.services import refresh_token, is_token_valid, login_async

from api.email_filtering_and_info_generation.services import get_all_reading_accounts, router
from api.email_authorization.services import update_authorization_uri
from api.email_filtering_and_info_generation.services import send_email_message,get_reading_emails_array

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow # type: ignore
from pathlib import Path

from googleapiclient.discovery import build 
from google.oauth2.credentials import Credentials
import os.path 
import base64 
from bs4 import BeautifulSoup 

import threading
import requests
import time
from dateutil.parser import isoparse


# email accounts array
email_acc_array = []

state_store = {}

last_email_read_time = ""


# input the email_acc_array and then return the updated email_acc_array
# email_acc_array=integrateEmail()




async def getEmails(id: int, new_email_msg_array, email_acc_address:str, last_email_read_time): 
    # Variable creds will store the user access token. 
    # If no valid token found, we will create one. 
    
    token_path = f'api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{id}/gmail_token.json'
    
    if (os.path.exists(token_path)):
        refresh_token(token_path)
    
    if not is_token_valid(token_path):
        
        await login_async(id, email_acc_address)
        
    
    while(not os.path.exists(token_path)):
        print("inside waiting loop")
        time.sleep(5)
    
    print("outside of waiting loop")
    creds = None
    
    SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.settings.basic'
    ]
    
    
    
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)


    # Connect to the Gmail API 
    service = build('gmail', 'v1', credentials=creds) 
    
    if last_email_read_time == "":
        # Calculate the timestamp for 10 minutes ago
        ten_minutes_ago = datetime.utcnow() - timedelta(minutes=600)
        ten_minutes_ago_unix = int(ten_minutes_ago.timestamp())
        
        # Request a list of all the messages received after the calculated timestamp
        result = service.users().messages().list(userId='me', q=f'after:{ten_minutes_ago_unix}').execute()        
        
    else:
        
        start_datetime_str = last_email_read_time
        start_datetime = datetime.strptime(start_datetime_str, "%a, %d %b %Y %H:%M:%S %z")

        # Convert the start_datetime to Unix timestamp
        start_timestamp = int(start_datetime.timestamp())
        
        # Request a list of all the messages received after the specified datetime
        result = service.users().messages().list(userId='me', q=f'after:{start_timestamp}').execute()
        
        
        
    messages = result.get('messages', []) 
    
   
    
    # messages is a list of dictionaries where each dictionary contains a message id
    # iterate through all the messages 
    for msg in messages: 
        # Get the message from its id 
        txt = service.users().messages().get(userId='me', id=msg['id']).execute() 
  
        # Use try-except to avoid any Errors 
        try: 
            # Get value of 'payload' from dictionary 'txt' 
            payload = txt['payload'] 
            headers = payload['headers'] 
            # Extract metadata
            metadata = {}
  
            # Look for Subject and Sender Email in the headers 
            # Iterate through headers to find relevant metadata
            for header in headers:
                if header['name'] == 'Date':
                    metadata['Received Time'] = header['value']
                    
                    # update the the last email read time, bcz the first email of the list is the latest one.
                    if messages[0]['id']==msg['id']:
                        last_email_read_time =  metadata['Received Time']
                        
                elif header['name'] == 'To':
                    metadata['Recipient'] = header['value']
                elif header['name'] == 'From':
                    metadata['Sender'] = header['value']
                elif header['name'] == 'Subject': 
                    subject = header['value']
                    
            # Extract email ID and thread ID
            metadata['Email ID'] = msg['id']
            metadata['Thread ID'] = msg['threadId']
            # The Body of the message is in Encrypted format. So, we have to decode it. 
            # Get the data and decode it with base 64 decoder. 
            parts = payload.get('parts')[0] 
            data = parts['body']['data'] 
            data = data.replace("-","+").replace("_","/") 
            decoded_data = base64.b64decode(data) 
  
            # Now, the data obtained is in lxml. So, we will parse  
            # it with BeautifulSoup library 
            soup = BeautifulSoup(decoded_data , "lxml") 
            # body = soup.body() 
            # body = soup.get_text()
            
            # Extract the text without HTML tags and Liquid markup
            body = re.sub(r'{%.*?%}', '', soup.get_text())  # Remove Liquid markup
            # Remove extra white spaces
            body = re.sub(r'\s+', ' ', body).strip()
            
            # Printing the subject, sender's email and message 
            #print("Subject: ", subject)       
            # print("Recipient:", metadata.get('Recipient'))
            # print("Sender:", metadata.get('Sender'))
            # print("Email ID:", metadata.get('Email ID'))
            # print("Thread ID:", metadata.get('Thread ID'))
            # print("Received Time:", metadata.get('Received Time'))
            #print("MESSAGE BODY: ", body) 
            # print('\n') 
            # print('\n') 
            
            email_msg_dict={"id": metadata.get('Email ID'),"time":metadata.get('Received Time'), "recipient": metadata.get('Recipient'), "sender": metadata.get('Sender'), "subject": subject,
                            "thread_id": metadata.get('Thread ID'), "body":body, "criticality_category":"", "our_sentiment_score":0, "products":[], "isSuggestion":False, "isIssue":False, "isInquiry":False}

            print("email_msg_dict", email_msg_dict)
            # append the new email msg dict to the new_email_msg_array
            print("appending a msg to the new email msg array")
            new_email_msg_array.append(email_msg_dict)
            
            print("new email msg array after appending", new_email_msg_array)
        except: 
            pass




async def read_all_new_emails_old_func(new_email_msg_array):
    
    #email_acc_array= await get_reading_emails_array()
    email_acc_array = [{'id': 1, 'address': 'raninduharischandra12@gmail.com', 'nickname': 'ranindu1'}]
    print("email_scc_array in read all new emails")
    print(email_acc_array)
    for email_acc in email_acc_array: 
        
    
         
        try:
            gmail = Gmail(client_secret_file=f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{email_acc['id']}/client_secret.json",
                    creds_file=f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{email_acc['id']}/gmail_token.json")

        except Exception as e:
            
            file_path =f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{email_acc['id']}/gmail_token.json"
            if os.path.exists(file_path):
                # Delete the file
                os.remove(file_path)
                
            time.sleep(5)
                
            gmail = Gmail(client_secret_file=f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{email_acc['id']}/client_secret.json",
                    creds_file=f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{email_acc['id']}/gmail_token.json")
        

        query_params = {
            "newer_than": (1, "day")
        }

        # get current time
        current_time = datetime.now(timezone.utc)
        print("Current time:", current_time)

        # get messages
        messages = gmail.get_messages(query=construct_query(query_params))
        for message in messages:

            # formatting message_incoming time
            message_incoming_time = datetime.strptime(message.date, "%Y-%m-%d %H:%M:%S%z")
            time_difference = current_time - message_incoming_time

            # calculating time difference
            time_difference_minutes = time_difference.total_seconds() / 60
            print("time difference in minutes")
            print(time_difference_minutes)

            # checking whether the msg came in the last 10 mins
            if abs(time_difference_minutes) <= 500:
                # print("Subject: " + message.subject)
                # print("To: " + message.recipient)
                # print("From: " + message.sender)
                # print("Subject: " + message.subject)
                # print("Date: " + message.date)
                # print("message incoming time", message_incoming_time)
                # make a new email_msg dictionary
                email_msg_dict={"id": message.id,"time":message_incoming_time, "recipient": message.recipient, "sender": message.sender, "subject": message.subject,
                                "thread_id": message.thread_id, "body":message.snippet, "criticality_category":"", "org_sentiment_score":0, "our_sentiment_score":0, "products":[], "isSuggestion":False, "isIssue":False, "isInquiry":False}

                 # append the new email msg dict to the new_email_msg_array
                print("appending a msg to the new email msg array")
                new_email_msg_array.append(email_msg_dict)

                # print("Preview: " + message.snippet)
                # print("Message Body: " + message.plain)

async def read_all_new_emails(new_email_msg_array, last_email_read_time):
    
    email_acc_array = await get_reading_emails_array()
    # email_acc_array = [{'id': 1, 'address': 'raninduharischandra12@gmail.com', 'nickname': 'ranindu1'}]
    

    
    for email_acc in email_acc_array: 
        
        await getEmails(email_acc["id"], new_email_msg_array, email_acc["address"], last_email_read_time)
        
        
    print("\n")
    print("\n")
    print("\n")
    print("\n")  
    #print("new email msg array after appending ALL", new_email_msg_array)   

    
    
async def push_new_emails_to_DB(new_email_msg_array):
    
    temp_email_msg_array = copy.deepcopy(new_email_msg_array)
    for temp_email_msg in temp_email_msg_array:
        del temp_email_msg["body"]
        await send_email_message(temp_email_msg)
    
async def repeat_every_10mins():

    
    # Continuously run the task every 'interval' seconds. 600 = 10 minutes.
    # this is currently set to 1 minute. change it later.
    print("it's happening")
    print("read_all_new_emails happening")
    new_email_msg_array = []
    last_email_read_time = ""
    await read_all_new_emails(new_email_msg_array, last_email_read_time)
    print("\n")
    print("\n")
    # print("RAW READ NEW EMAIL MESG ARRAY", new_email_msg_array)
    mask_email_messages(new_email_msg_array)
    #print("MASKED EMAIL MESSAGES", new_email_msg_array)
    # await format_email_bodies(new_email_msg_array)
    # print("\n")
    # print("\n formatted email bodies")
    # print("\n")
    # print("formatted EMAIL BODIES----------",new_email_msg_array)
    # identify_sentiments(new_email_msg_array)
    # identify_criticality(new_email_msg_array)
    # print("\n")
    # print("\n criticality identified emails")
    # print("\n")
    # print(new_email_msg_array)
    # # #await identify_notifcations(new_email_msg_array)
    # await identify_topics(new_email_msg_array)
    # print("\n")
    # print("\n Products identified emails")
    # print("\n")
    # print("emails with topics",new_email_msg_array)
    # # # print(new_email_msg_array)
    # # #print(new_email_msg_array)
    # await identify_issues_inquiries_and_checking_status(new_email_msg_array) # make sure to perform this before the coversations_summarizing
    # # print("---------------------------------------finished identify issues------------------------------")
    # print("\n")
    # print("\n Issues and Inquiries identified emails")
    # print("\n")
    # print(new_email_msg_array)
    # await identify_and_summarize_suggestions(new_email_msg_array)
    # print("\n")
    # print("\n Suggestions identified emails")
    # print("\n")
    # print(new_email_msg_array)
    # # print("---------------------------------------finished identifying summaries------------------------")
    # # print(new_email_msg_array)
    # await push_new_emails_to_DB(new_email_msg_array)
    # print("database update successful")
    summarize_conversations(new_email_msg_array)
    print("conversation summaries identified")
    
    # make this 10 minutes
    interval = 60
    next_time = time.time() + interval
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            print("read_all_new_emails happening")
            new_email_msg_array = []
            await read_all_new_emails(new_email_msg_array)
            #print(new_email_msg_array)
            mask_email_messages(new_email_msg_array)
            format_email_bodies(new_email_msg_array)
            identify_sentiments(new_email_msg_array)
            identify_criticality(new_email_msg_array)
            #print(new_email_msg_array)
            await identify_notifcations(new_email_msg_array)
            # print(new_email_msg_array)
            identify_topics(new_email_msg_array)
            print(new_email_msg_array)
            await push_new_emails_to_DB(new_email_msg_array)
            
            await identify_issues_inquiries_and_checking_status(new_email_msg_array) # make sure to perform this before the coversations_summarizing
            await summarize_conversations(new_email_msg_array)
            await identify_and_summarize_suggestions(new_email_msg_array)
            
        except Exception as e:
            print("Error:", e)
        # Calculate the next execution time
        next_time += (time.time() - next_time) // interval * interval + interval















































#
#         with open("email_samples.txt", "a") as f:
#             if message.plain:
#                 if len(message.plain)<1000:
#                     f.write(message.plain)
#
#
