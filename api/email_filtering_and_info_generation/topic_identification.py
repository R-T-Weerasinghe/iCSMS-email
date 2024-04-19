from langchain_google_genai import ChatGoogleGenerativeAI
from api.email_filtering_and_info_generation.config import API_KEY  
import google.generativeai as genai
import os
import json

os.environ['GOOGLE_API_KEY'] = API_KEY


# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)



# topics list
topics = ['business','products', 'marketing issues', 'assignments', 'education', 'UN', 'AI']


def identify_topics(new_email_msg_array):
    
    for new_email_msg in new_email_msg_array:
        
        new_topics_arr=[]
        
        # for topic in topics:
            
        #     topics_script = f"""if this email '{new_email_msg["body"]}'
        #                         belong to the topic '{topic}', output the true. otherwise output false. Don't output anything other than true or false."""

           

        #     # Send the email body to Gemini for criticality identification
        #     response = llm.invoke(topics_script2)
        #     print(response.content)
        #     # if(response.content=="true"):
        #     #     new_topics_arr.append(topic)
            
            
        topics_script2 = f"""if this email '{new_email_msg["body"]}'
                                belong to any of the following topics list '{topics}', output the matched topics as a list which is in the following format '["topic1", "topic2"]'. Don't output anything other than matched topics list. if no topics are matched output and empty list like this '[]'"""    
         
        response = llm.invoke(topics_script2)  
        
        new_topics_arr = json.loads(response.content)
        print(new_topics_arr)
        
        new_email_msg["topics"] = new_topics_arr