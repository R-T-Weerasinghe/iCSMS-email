
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


# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7,api_key=google_api_key)


async def summarize_conversations(new_email_msg_array):
    
    # Query to get all thread_ids
    thread_ids = collection_conversations.find({}, {'thread_id': 1, '_id': 0})
    
    # Convert the query result to a list of thread_ids
    thread_id_list = [doc['thread_id'] for doc in thread_ids]
    
    
    new_convo_summaries_array = []
    
    for new_email_msg in new_email_msg_array:
        
        email_ids=[]
        
        full_convo_text = ""
        
        if new_email_msg["thread_id"] in thread_id_list:
            
            convo_summary_doc = collection_conversations.find_one({'thread_id': new_email_msg["thread_id"]})
            prev_summary = convo_summary_doc['summary']
            
            full_convo_text = new_email_msg["body"] + " " + prev_summary
            
            convo_summary_doc['updated_times'] = convo_summary_doc['updated_times'].append(new_email_msg["time"])
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
        
        if new_email_msg["thread_id"] in thread_id_list:
             await update_summary(new_email_msg["thread_id"], response.content, new_updated_times)
        
        else:
        
            new_convo_summary = Convo_summary(
                                thread_id=new_email_msg["thread_id"], 
                                subject = new_email_msg["subject"], 
                                updated_times= [new_email_msg["time"]], 
                                summary=response.content,
                                products=new_email_msg["products"])
            
            await send_convo_summary(new_convo_summary)
        
        
        
        
        
        
        