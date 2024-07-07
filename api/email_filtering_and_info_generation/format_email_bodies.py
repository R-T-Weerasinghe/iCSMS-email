from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7,api_key=google_api_key)


async def format_email_bodies(new_email_msg_array):
    
    for new_email_msg in new_email_msg_array:
        
        # email_body_formating_script = f""" "{new_email_msg['body']}" 
        #                               Extract the real email body from the above text. 
        #                               The real email body is either between the start of the text and 
        #                               the first occurrence of a line containing "On" followed by a space, a date, "at", a time. 
        #                               OR if such format is not present, then the whole text can be considered as 
        #                               the real email body. ONLY OUTPUT the real email body. Don't output anything else. 
        #                               NO NEED OF OUTPUTING ANY EXPLANATIONS."""
        
        
        email_body_formating_script = f""" "{new_email_msg['body']}" 
                                     Extract text before "On" (date, time).
                                     If the above format is not found, consider the entire text as the extracted text.\
                                     Only output the extracted text. Don't output anything else."""
        
        response = llm.invoke(email_body_formating_script)
        extracted_email_body = response.content
        
        new_email_msg['body'] = extracted_email_body
        