
from langchain_google_genai import ChatGoogleGenerativeAI
from api.email_filtering_and_info_generation.models import Convo_summary
from api.email_filtering_and_info_generation.services import send_convo_summary, update_summary
 
import google.generativeai as genai
import os
from dotenv import load_dotenv

from api.email_filtering_and_info_generation.configurations.database import collection_conversations



# Load environment variables from .env file
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
google_api_key_2 = os.getenv("GOOGLE_API_KEY_2")

google_api_key_4 = os.getenv("GOOGLE_API_KEY_4")
google_api_key_5 = os.getenv("GOOGLE_API_KEY_5")
google_api_key_6 = os.getenv("GOOGLE_API_KEY_6")




async def summarize_conversations(new_email_msg_array):
    
    i=0 
    
    for new_email_msg in new_email_msg_array:
        
        if(i%3==0):
            os.environ["GOOGLE_API_KEY"] = google_api_key_4
            llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7,api_key=google_api_key)
        elif(i%3==1): 
            
            os.environ["GOOGLE_API_KEY"] = google_api_key_5
            llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7,api_key=google_api_key)
        else:
            os.environ["GOOGLE_API_KEY"] = google_api_key_6
            llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7,api_key=google_api_key) 
                
        i = i+1
        # Query to get all thread_ids
        
        try:
            document = collection_conversations.find_one({'thread_id': new_email_msg["thread_id"]})
            
            
            full_convo_text = ""
            
            if document:
                
                convo_summary_doc = document
                prev_summary = convo_summary_doc['summary']
                
                full_convo_text = new_email_msg["body"] + " " + prev_summary
                
                convo_summary_doc['updated_times'].append(new_email_msg["time"])
                new_updated_times = convo_summary_doc['updated_times'] 
                
            else:
                
                full_convo_text = new_email_msg["body"]
            
        
            
            
            conversation_summarizing_script = f"""Write a summary of this text '{full_convo_text}'. The summary should summarize what the above email conversation is about and 
            it shoudl be able to give the reader an undersating about the email conversation in a very short time. Also, only output the summary. 
            Don't output anything else.These emails are either ones that came to a customer care email account of a company, or the emails sent by that company to their customers, so provide the summary as you are summarzing these to a company manager. """
            
            # Send the full convo text to Gemini for summarizing
            response = llm.invoke(conversation_summarizing_script)  
            
            print("\n")
            print("summary")
            print(response.content)   
            print("\n") 
            
            # at last adding the new_email_id to the array
            
            if document:
                await update_summary(new_email_msg["thread_id"], response.content, new_updated_times)
            
            else:
            
                new_convo_summary = Convo_summary(
                                    thread_id=new_email_msg["thread_id"], 
                                    subject = new_email_msg["subject"], 
                                    updated_times= [new_email_msg["time"]], 
                                    summary=response.content,
                                    products=new_email_msg["products"])
                
                print("sent thread summary")
                #await send_convo_summary(new_convo_summary)
                
        except Exception as e:
            
            print("Exception : ", e)
            print("Summary identiifcation skipped in the ", 1, " email")
        
        
        
        
        
        