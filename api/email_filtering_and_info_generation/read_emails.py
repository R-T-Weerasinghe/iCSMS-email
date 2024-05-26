import copy
import os
import asyncio

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




from api.email_filtering_and_info_generation.routes import router
from api.email_filtering_and_info_generation.routes import send_email_message,get_reading_emails_array

import threading
import time


# email accounts array
email_acc_array = []


# input the email_acc_array and then return the updated email_acc_array
# email_acc_array=integrateEmail()


async def read_all_new_emails(new_email_msg_array):
    
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
    await read_all_new_emails(new_email_msg_array)
    #print(new_email_msg_array)
    mask_email_messages(new_email_msg_array)
    # print(new_email_msg_array)
    format_email_bodies(new_email_msg_array)
    print(new_email_msg_array)
    identify_sentiments(new_email_msg_array)
    identify_criticality(new_email_msg_array)
    #print(new_email_msg_array)
    #await identify_notifcations(new_email_msg_array)
    identify_topics(new_email_msg_array)
    #print("emails with topics",new_email_msg_array)
    # print(new_email_msg_array)
    #print(new_email_msg_array)
    await identify_issues_inquiries_and_checking_status(new_email_msg_array) # make sure to perform this before the coversations_summarizing
    print("---------------------------------------finished identify issues------------------------------")
    print(new_email_msg_array)
    await identify_and_summarize_suggestions(new_email_msg_array)
    print("---------------------------------------finished identifying summaries------------------------")
    print(new_email_msg_array)
    await push_new_emails_to_DB(new_email_msg_array)
    await summarize_conversations(new_email_msg_array)
    print("database update successful")
    
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
