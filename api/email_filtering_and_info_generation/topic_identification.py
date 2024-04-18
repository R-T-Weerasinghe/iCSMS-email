from langchain_google_genai import ChatGoogleGenerativeAI
from api.email_filtering_and_info_generation.config import API_KEY  
import google.generativeai as genai
import os

os.environ['GOOGLE_API_KEY'] = API_KEY


# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)



# topics list
topics = ['business','products', 'marketing issues', 'assignments', 'education', 'UN', 'AI']


def identify_topics(new_email_msg_array):
    
    for new_email_msg in new_email_msg_array:
        
        new_topics_arr=[]
        
        for topic in topics:
            
            topics_script = f"""if this email '{new_email_msg}'
                                belong to the topic '{topic}', output the true. otherwise output false. Don't output anything other than true or false."""



            # Send the email body to Gemini for criticality identification
            response = llm.invoke(topics_script)
            print(response)
            if(response.content=="true"):
                new_topics_arr.append(topic)
                
        
        new_email_msg["topics"] = new_topics_arr