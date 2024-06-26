import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from api.email_filtering_and_info_generation.config import API_KEY  
import google.generativeai as genai
import os
from api.email_filtering_and_info_generation.services import getProductsList
from dotenv import load_dotenv
import json


load_dotenv()

    
# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)



# topics list




async def identify_topics(new_email_msg_array):
    
    products = await getProductsList()
    print("product list retainded     :", products)
    if products!=[]:
    
        for new_email_msg in new_email_msg_array:
            
            new_products_arr=[]
            
            # for topic in topics:
                
            #     topics_script = f"""if this email '{new_email_msg["body"]}'
            #                         belong to the topic '{topic}', output the true. otherwise output false. Don't output anything other than true or false."""

            

            #     # Send the email body to Gemini for criticality identification
            #     response = llm.invoke(topics_script2)
            #     print(response.content)
            #     # if(response.content=="true"):
            #     #     new_topics_arr.append(topic)
                
                
            products_script2 = f"""if this email '{new_email_msg["body"]}'
                                    is regarding any of the products in the following products list '{products}', output the matched products as a list which is in the following format '["product1", "product2"]'. Don't output anything other than matched products list. if no products are matched output and empty list like this '[]'"""    
            
            response = llm.invoke(products_script2)  
            
            new_products_arr = json.loads(response.content)
            print("identified products for this email    :",new_products_arr)
            
            new_email_msg["products"] = new_products_arr