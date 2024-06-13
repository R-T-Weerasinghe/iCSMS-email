from datetime import datetime, timedelta, timezone
import random
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from api.email_filtering_and_info_generation.configurations.database import collection_notificationSendingChannels,collection_email_msgs,collection_inquiries,collection_issues, collection_readingEmailAccounts, collection_configurations
from api.dashboard import services

router = APIRouter()


# send current reading emails to frontend   
@router.get("/dashboard/get_current_overall_sentiments/{user_id}")
async def get_current_overall_sentiments(intervalIndays: int):
 
    
   
    result = await services.get_current_overall_sentiments(intervalIndays)
    return JSONResponse(content=result)




@router.get("/dashboard/get_data_for_topic_cloud")
async def get_data_for_topic_cloud(intervalIndays: int):
    
    result = await services.get_data_for_topic_cloud(intervalIndays)
    return JSONResponse(content=result)


@router.get("/dashboard/get_data_for_word_cloud")
async def get_data_for_word_cloud(intervalIndays: int):
    
    result = await services.get_data_for_word_cloud(intervalIndays)
    return JSONResponse(content=result)

 
@router.get("/dashboard/get_data_for_stat_cards")
async def get_data_for_stat_cards(intervalIndays: int):
    
    result = await services.get_data_for_stat_cards(intervalIndays)    
    return JSONResponse(content=result)


@router.get("/dashboard/get_data_for_sentiments_by_topic")
async def get_data_for_sentiments_by_topic(intervalIndays: int):
    
    result = await services.get_data_for_sentiments_by_topic(intervalIndays)
    return JSONResponse(content=result)


@router.get("/dashboard/get_data_for_sentiments_by_time")
async def get_data_for_sentiments_by_time(intervalIndays: int):
    
    result = await services.get_data_for_sentiments_by_time(intervalIndays)    
    return JSONResponse(content=result)



@router.get("/dashboard/get_data_for_sentiments_distribution_of_topics")
async def get_data_for_sentiments_distribution_of_topics(intervalIndays: int):
    
    
    result = await services.get_data_for_sentiments_distribution_of_topics(intervalIndays)
    return JSONResponse(content=result)
            

@router.get("/dashboard/get_data_value_for_gauge_chart")
async def get_data_value_for_gauge_chart(intervalIndays: int):
    
    result = await services.get_data_value_for_gauge_chart(intervalIndays)
    return JSONResponse(content=result)


            
@router.get("/dashboard/get_data_for_issue_and_inquiry_frequency_by_products")
async def get_data_for_issue_and_inquiry_frequency_by_products(intervalIndays: int):
    
    result = await services.get_data_for_issue_and_inquiry_frequency_by_products(intervalIndays)
    return JSONResponse(content=result)   
        
@router.get("/dashboard/get_data_for_frequency_by_issue_type_and_inquiry_types")
async def get_data_for_frequency_by_issue_type_and_inquiry_types(intervalIndays: int):


    result = await services.get_data_for_frequency_by_issue_type_and_inquiry_types(intervalIndays)
    return JSONResponse(content=result)  
        

@router.get("/dashboard/get_data_for_issue_frequency_by_efficiency_and_effectiveness")
async def get_data_for_issue_frequency_by_efficiency_and_effectiveness(intervalIndays: int):     
     
    result = await services.get_data_for_issue_frequency_by_efficiency_and_effectiveness(intervalIndays)   
    return JSONResponse(content=result)   
 


@router.get("/dashboard/get_data_for_inquiry_frequency_by_efficiency_and_effectiveness")
async def get_data_for_inquiry_frequency_by_efficiency_and_effectiveness(intervalIndays: int):     
    
    result = services.get_data_for_inquiry_frequency_by_efficiency_and_effectiveness(intervalIndays)    
    return JSONResponse(content=result)    


@router.get("/dashboard/get_data_for_overall_efficiency_and_effectiveness_percentages")
async def get_data_for_overall_efficiency_and_effectiveness_percentages(intervalIndays: int):  
        
    result = services.get_data_for_overall_efficiency_and_effectiveness_percentages(intervalIndays)
    return JSONResponse(content=result)


            
@router.get("/dashboard/get_data_for_ongoing_and_closed_stats")
async def get_data_for_ongoing_and_closed_stats(intervalIndays: int):
    
    result = services.get_data_for_ongoing_and_closed_stats(intervalIndays)  
    return JSONResponse(content=result)        

 

@router.get("/dashboard/get_data_for_best_performing_email_acc")
async def get_data_for_best_performing_email_acc(intervalIndays: int):
    
    result = services.get_data_for_best_performing_email_acc(intervalIndays)     
    return JSONResponse(content=result)

        
        
@router.get("/dashboard/get_data_for_efficiency_by_email_acc")
async def get_data_for_efficiency_by_email_acc(intervalIndays: int):  
     
    result = services.get_data_for_efficiency_by_email_acc(intervalIndays)        
    return JSONResponse(content=result)
            
            

@router.get("/dashboard/get_data_for_overdue_issues")
async def get_data_for_overdue_issues(intervalIndays: int):           

    result = services.get_data_for_overdue_issues(intervalIndays)           
    return JSONResponse(content=result)          
        




