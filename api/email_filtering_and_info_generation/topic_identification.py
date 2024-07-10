import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from api.email_filtering_and_info_generation.config import API_KEY  
import google.generativeai as genai
import os
from api.email_filtering_and_info_generation.services import getProductsList
from dotenv import load_dotenv
import json


load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
google_api_key_2 = os.getenv("GOOGLE_API_KEY_2")

google_api_key_4 = os.getenv("GOOGLE_API_KEY_4")
google_api_key_5 = os.getenv("GOOGLE_API_KEY_5")
google_api_key_6 = os.getenv("GOOGLE_API_KEY_6")
    




# topics list




async def identify_topics(new_email_msg_array):
    i=0
    products = await getProductsList()
    print("product list retainded     :", products)
    if products!=[]:
    
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
            
            new_products_arr=[]
            
            # for topic in topics:
                
            #     topics_script = f"""if this email '{new_email_msg["body"]}'
            #                         belong to the topic '{topic}', output the true. otherwise output false. Don't output anything other than true or false."""

            

            #     # Send the email body to Gemini for criticality identification
            #     response = llm.invoke(topics_script2)
            #     print(response.content)
            #     # if(response.content=="true"):
            #     #     new_topics_arr.append(topic)
                
                
            products_script2 = f"""Given the following email body:

                                    "{new_email_msg["body"]}"

                                    And the list of products offered by the company:

                                    "{products}"

                                    Identify which products are mentioned in the email. Output the matched products as a list in the format: '["product1", "product2"]'. 
                                    If no products are matched, output an empty list: '[]'. 
                                    Usually each email is regarding one of the products so look carefully for products mentioned."""    
            
            response = llm.invoke(products_script2)  
            
            new_products_arr = json.loads(response.content)
            print("identified products for this email    :",new_products_arr)
            
            new_email_msg["products"] = new_products_arr