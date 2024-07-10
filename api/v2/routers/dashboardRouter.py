from datetime import datetime, timedelta, timezone
import random
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from api.v2.models.dashboardModel import BestPerformingEmailAccResponse, EmailAccEfficiencyResponse, GaugeChartResponse, InquiriesByEfficiencyEffectivenessResponse, IssueInquiryFreqByProdcutsResponse, IssueInquiryFreqByTypeResponse, IssuesByEfficiencyEffectivenessResponse, OngoingAndClosedStatsResponse, OverallyEfficiencyEffectivenessPecentagesResponse, OverdueIssuesResponse, SentimentsByTimeResponse, SentimentsByTopicResponse, SentimentsDistributionByTimeResponse, GetCurrentOverallSentimentProgress, StatCardSingleResponse, TimeGraph, WordCloudSingleResponse
from api.v2.dependencies.database import collection_notificationSendingChannels,collection_email_msgs,collection_inquiries,collection_issues, collection_readingEmailAccounts, collection_configurations

from api.v2.services import dashboardService as services
from api.v2.services.dashboardService import getTimeData
from api.v2.models.dashboardModel import TimeDataResponse
router = APIRouter()


@router.get("/dashboard/")
async def get_dashboard():
    return {"message": "Welcome to email/v2/dashboard dashboard page"}

@router.get("/dashboard/time-graph", response_model=TimeDataResponse)
async def get_time_data(intervalInDaysStart: int, intervalInDaysEnd:int):
    result = await getTimeData(intervalInDaysStart, intervalInDaysEnd)
    return result

@router.get("/dashboard/get_current_overall_sentiments", response_model=GetCurrentOverallSentimentProgress)
async def get_current_overall_sentiments(intervalInDaysStart: int, intervalInDaysEnd:int):
   
    result = await services.get_current_overall_sentiments(intervalInDaysStart, intervalInDaysEnd)
    print("CURRENT OVERALL SENTIMENTS",result)
    return result



@router.get("/dashboard/get_data_for_word_cloud", response_model=List[WordCloudSingleResponse])
async def get_data_for_word_cloud(intervalInDaysStart: int, intervalInDaysEnd:int):
    
    result = await services.get_data_for_word_cloud(intervalInDaysStart, intervalInDaysEnd)
    return result

 
@router.get("/dashboard/get_data_for_stat_cards", response_model= List[StatCardSingleResponse] )
async def get_data_for_stat_cards(intervalInDaysStart: int, intervalInDaysEnd:int):
    
    result = await services.get_data_for_stat_cards(intervalInDaysStart, intervalInDaysEnd)    
    return result


@router.get("/dashboard/get_data_for_sentiments_by_topic", response_model= SentimentsByTopicResponse)
async def get_data_for_sentiments_by_topic(intervalInDaysStart: int, intervalInDaysEnd:int):
    
    result = await services.get_data_for_sentiments_by_topic(intervalInDaysStart, intervalInDaysEnd)
    return result


@router.get("/dashboard/get_data_for_sentiments_by_time", response_model= SentimentsByTimeResponse)
async def get_data_for_sentiments_by_time(intervalInDaysStart: int, intervalInDaysEnd:int):
    
    result = await services.get_data_for_sentiments_by_time(intervalInDaysStart, intervalInDaysEnd)    
    return result



@router.get("/dashboard/get_data_for_sentiments_distribution_of_topics", response_model= SentimentsDistributionByTimeResponse)
async def get_data_for_sentiments_distribution_of_topics(intervalInDaysStart: int, intervalInDaysEnd:int):
    
    
    result = await services.get_data_for_sentiments_distribution_of_topics(intervalInDaysStart, intervalInDaysEnd)
    return result
            

@router.get("/dashboard/get_data_value_for_gauge_chart", response_model= GaugeChartResponse)
async def get_data_value_for_gauge_chart(intervalInDaysStart: int, intervalInDaysEnd:int):
    
    result = await services.get_data_value_for_gauge_chart(intervalInDaysStart, intervalInDaysEnd)
    return result


            
@router.get("/dashboard/get_data_for_issue_and_inquiry_frequency_by_products", response_model = IssueInquiryFreqByProdcutsResponse)
async def get_data_for_issue_and_inquiry_frequency_by_products(intervalInDaysStart: int, intervalInDaysEnd:int):
    
    result = await services.get_data_for_issue_and_inquiry_frequency_by_products(intervalInDaysStart, intervalInDaysEnd)
    print(result)
    return result   
        
@router.get("/dashboard/get_data_for_frequency_by_issue_type_and_inquiry_types", response_model =IssueInquiryFreqByTypeResponse)
async def get_data_for_frequency_by_issue_type_and_inquiry_types(intervalInDaysStart: int, intervalInDaysEnd:int):


    result = await services.get_data_for_frequency_by_issue_type_and_inquiry_types(intervalInDaysStart, intervalInDaysEnd)
    print(result)
    return result  
        

@router.get("/dashboard/get_data_for_issue_frequency_by_efficiency_and_effectiveness", response_model = IssuesByEfficiencyEffectivenessResponse)
async def get_data_for_issue_frequency_by_efficiency_and_effectiveness(intervalInDaysStart: int, intervalInDaysEnd:int):     
     
    result = await services.get_data_for_issue_frequency_by_efficiency_and_effectiveness(intervalInDaysStart, intervalInDaysEnd)   
    print(result)
    return result   
 


@router.get("/dashboard/get_data_for_inquiry_frequency_by_efficiency_and_effectiveness", response_model = InquiriesByEfficiencyEffectivenessResponse)
async def get_data_for_inquiry_frequency_by_efficiency_and_effectiveness(intervalInDaysStart: int, intervalInDaysEnd:int):     
    
    result = await services.get_data_for_inquiry_frequency_by_efficiency_and_effectiveness(intervalInDaysStart, intervalInDaysEnd)    
    return result    


@router.get("/dashboard/get_data_for_overall_efficiency_and_effectiveness_percentages", response_model = OverallyEfficiencyEffectivenessPecentagesResponse)
async def get_data_for_overall_efficiency_and_effectiveness_percentages(intervalInDaysStart: int, intervalInDaysEnd:int):  
        
    result = await services.get_data_for_overall_efficiency_and_effectiveness_percentages(intervalInDaysStart, intervalInDaysEnd)
    print("overall efficienct and effec data-------------------", result)
    return result


            
@router.get("/dashboard/get_data_for_ongoing_and_closed_stats", response_model = OngoingAndClosedStatsResponse)
async def get_data_for_ongoing_and_closed_stats(intervalInDaysStart: int, intervalInDaysEnd:int):
    
    result = await services.get_data_for_ongoing_and_closed_stats(intervalInDaysStart, intervalInDaysEnd)  
    return result        

 

@router.get("/dashboard/get_data_for_best_performing_email_acc", response_model = BestPerformingEmailAccResponse)
async def get_data_for_best_performing_email_acc(intervalInDaysStart: int, intervalInDaysEnd:int):
    
    result = await services.get_data_for_best_performing_email_acc(intervalInDaysStart, intervalInDaysEnd)     
    return result

        
        
@router.get("/dashboard/get_data_for_efficiency_by_email_acc", response_model = EmailAccEfficiencyResponse)
async def get_data_for_efficiency_by_email_acc(intervalInDaysStart: int, intervalInDaysEnd:int):  
     
    result = await services.get_data_for_efficiency_by_email_acc(intervalInDaysStart, intervalInDaysEnd)        
    return result
            
            

@router.get("/dashboard/get_data_for_overdue_issues", response_model = OverdueIssuesResponse)
async def get_data_for_overdue_issues(intervalInDaysStart: int, intervalInDaysEnd:int):           

    result = await services.get_data_for_overdue_issues(intervalInDaysStart, intervalInDaysEnd)           
    return result          
        

@router.get("/dashboard/first-response-time", response_model=TimeGraph)
async def get_first_response_time(intervalInDaysStart: int, intervalInDaysEnd:int):
    result = await services.getFirstResponseTime(intervalInDaysStart, intervalInDaysEnd)
    return result


@router.get("/dashboard/resolution-time", response_model=TimeGraph)
async def get_resolution_time(intervalInDaysStart: int, intervalInDaysEnd:int):
    result = await services.getResolutionTime(intervalInDaysStart, intervalInDaysEnd)
    return result