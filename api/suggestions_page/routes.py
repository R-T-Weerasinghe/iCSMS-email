from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from api.settings.models import IntergratingEmailData, NotiSendingChannelsRecord
from typing import Dict, Any
from api.email_filtering_and_info_generation.emailIntegration import integrateEmail
from api.email_filtering_and_info_generation.configurations.database import  collection_suggestions,collection_readingEmailAccounts, collection_configurations
from api.email_filtering_and_info_generation.routes import get_reading_emails_array
from api.settings.models import Trigger
from fastapi.responses import JSONResponse
import shutil



router = APIRouter()


# filtered suggestions listener
@router.get("/suggestion-filtering/get_filtered_suggestions")
def get_filtered_suggestions(intervalIndays: int, productSelected: str, recipientEmailSelected: str):
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)
    
    if productSelected=="" and recipientEmailSelected=="":
        query = {
            "date": {"$gte": n_days_ago}
        }  
    elif productSelected=="":
        query = {
            "recepient": recipientEmailSelected,
            "date": {"$gte": n_days_ago}
        }  
    elif recipientEmailSelected=="":
        query = {
            "products": {"$elemMatch": {"$eq": productSelected}},
            "date": {"$gte": n_days_ago}
        }          
    else:
        query = {
            "recepient": recipientEmailSelected,
            "products": {"$elemMatch": {"$eq": productSelected}},
            "date": {"$gte": n_days_ago}
        }
    
    
    
    suugestions_query_result = collection_suggestions.find(query)
    
    suggestions_dict_list = []
    
    if suugestions_query_result:
        
        for doc in suugestions_query_result:
            
            # remove the timezone part
            dt = datetime.fromisoformat(doc["date"][:-6])
            # Extract the date in "yyyy-mm-dd" format
            date_str = dt.date().isoformat()
            
            suggestion = {"receiver":doc["recepient"], "date":date_str, "products":doc["products"], 
                          "suggestion":doc["suggestion"]}
            
            suggestions_dict_list.append(suggestion)
            
    
    result = {"suggestionsData": suggestions_dict_list} 
    return JSONResponse(content=result)    

@router.get("/suggestion-filtering/get_all_recepients")
async def get_all_recepients():
    
    recepients = []
    cursor = collection_readingEmailAccounts.find()
    
    for doc in cursor:
        recepients.append(doc["address"])
    
    result = {"recepients", recepients}
    return JSONResponse(content=result)  

@router.get("/suggestion-filtering/get_all_products")
async def get_all_products():
    
    products=[]
    
    cursor_doc = collection_configurations.find({"id":1})
    
    if cursor_doc:
        products = cursor_doc.get("products", [])
    
    result = {"products":products}
    return JSONResponse(content=result) 
    
    
    
    
    
    
