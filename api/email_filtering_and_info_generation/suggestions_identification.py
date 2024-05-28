from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from dotenv import load_dotenv
import os

from api.email_filtering_and_info_generation.routes import send_suggestion

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7,api_key=google_api_key)

async def identify_and_summarize_suggestions(new_email_msg_array):
    
    
    for new_email_msg in new_email_msg_array:
        
        identification_script = f""" '{new_email_msg["body"]}' 
                                if this customer care inbox email is a suggestion by a 
                                customer to a specific company please output yes, 
                                otherwise output no. Don't output anything other than yes or no."""
                                
        # Send the email body to Gemini for suggestion identification
        response = llm.invoke(identification_script)
        
        # update the isSuggestion
        if("yes"==response.content):
            new_email_msg["isSuggestion"]=True
    
            suggestion_summarizing_script = f""" '{new_email_msg["body"]}' 
                                    summarize the above suggestion given by the customer to one or two lines. 
                                    (minimum one line. maximum two lines.) Only output the summarized suggestion. 
                                    when writing the suggestion don't put parts like "customer suggests". 
                                    only include the suggestion.  """
            
            # Send the email body to Gemini for suggestion summarization
            response = llm.invoke(suggestion_summarizing_script)
            
            suggestion ={"email_id": new_email_msg["id"], "suggestion":response.content, "products":new_email_msg["products"],
                         "date":new_email_msg["time"], "recepient":new_email_msg["recipient"]}
            

            # send the new suggestion to the Suggestions collection
            await send_suggestion(suggestion)
            
            
            
            
            
            
            
            