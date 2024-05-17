
stored_emails=[{"id": 5, "recipient": "raninduharischandra12@gmail.com", "sender": message.sender, "subject": message.subject,
                                "thread_id": '18e4a6f934ebf277', "body":message.plain, "criticality_category":"", "org_sentiment_score":0, "our_sentiment_score":0},
               {"id": 6, "recipient": "raninduharischandra12@gmail.com", "sender": message.sender, "subject": message.subject,
                                "thread_id": '18e4a6f934ebf277', "body":message.plain, "criticality_category":"", "org_sentiment_score":0, "our_sentiment_score":0},
               {"id": 7, "recipient": "raninduharischandra12@gmail.com", "sender": message.sender, "subject": message.subject,
                                "thread_id": '19E78888IL90', "body":message.plain, "criticality_category":"", "org_sentiment_score":0, "our_sentiment_score":0}]
from langchain_google_genai import ChatGoogleGenerativeAI
from config import API_KEY  
import google.generativeai as genai
import os

from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")


# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7,api_key=google_api_key)


def summarize_conversations(new_email_msg_array):
    
    new_convo_summaries_array = []
    
    for new_email_msg in new_email_msg_array:
        
        email_ids=[]
        
        full_convo_text = ""
        
        # adding all the emails of the same thread_id together, even the recently stored new_email_msg body is added from here
        # check again to make sure the emails bodies and ids are added in order
        for stored_email in stored_emails:
            
            if stored_email["thread_id"]==new_email_msg["thread_id"]:
                
                full_convo_text = full_convo_text + "/n" + stored_email["body"]
                
                # collecting email ids in order
                email_ids.append(stored_email["id"])
    
        
        
        conversation_summarizing_script = f"Write a summary of this text '{full_convo_text}'. The summary should summarize what the above email conversation is about and 
        it shoudl be able to give the reader an undersating about the email conversation in a very short time. Also, only output the summary. Don't output anything else."
        
        # Send the full convo text to Gemini for summarizing
        response = llm.invoke(conversation_summarizing_script)      
        
        # at last adding the new_email_id to the array
        
        
        new_convo_summary = {"thread_id":new_email_msg["thread_id"], "subject":new_email_msg["subject"], "summary":response.content,
                              "email_ids":email_ids}
        
        