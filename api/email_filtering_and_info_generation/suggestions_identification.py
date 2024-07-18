from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from dotenv import load_dotenv
import os

from api.email_filtering_and_info_generation.services import send_suggestion

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
google_api_key_2 = os.getenv("GOOGLE_API_KEY_2")

google_api_key_4 = os.getenv("GOOGLE_API_KEY_4")
google_api_key_5 = os.getenv("GOOGLE_API_KEY_5")
google_api_key_6 = os.getenv("GOOGLE_API_KEY_6")



async def identify_and_summarize_suggestions(new_email_msg_array):
    
    i = 0
    for new_email_msg in new_email_msg_array:
        
        if new_email_msg["type"] == "client":
        
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
            
            try:
            
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
                    
                    suggestion ={"suggestion":response.content, "products":new_email_msg["products"],
                                "date":new_email_msg["time"], "recepient":new_email_msg["recipient"]}
                    

                    # send the new suggestion to the Suggestions collection
                    await send_suggestion(suggestion)
                    new_email_msg["isSuggestion"] = True
                    
                    print("suggestion Identified. \n")
                
                
                else:
                    
                    print("no suggestion identified in this email")
                    
            except Exception as e:
                
                print("Excepteion :", e)
                print(i, "th email number is skipped from identifyinh suggestions")   
                
            
            
            
            
            
            
            
            