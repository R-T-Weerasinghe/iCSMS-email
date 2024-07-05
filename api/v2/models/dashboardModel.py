
    
from typing import List, Union
from pydantic import BaseModel
from datetime import datetime

class GetCurrentOverallSentimentProgress(BaseModel):
    positive_percentage:float
    neutral_percentage:float
    negative_percentage:float
    
class WordCloudSingleResponse(BaseModel):
    topic: str
    frequency: int
    color: str
    
class StatCardSingleResponse(BaseModel):
    title: int
    sub_title: str
    header: str
    sentiment: str
    imgPath: str
    
    
class SentimentsByTopicResponse(BaseModel):
    sbtChartLabels: List[str]
    sbtChartColors: List[str]
    sbtChartValues: List[float]
    
class SentimentsByTimeResponse(BaseModel):
    labels: List[str]
    positive_values: List[Union[float, None]]
    neutral_values: List[Union[float, None]]
    negative_values: List[Union[float, None]]
    
class SentimentsDistributionByTimeResponse(BaseModel):   
    labels_freq: List[str]
    positive_values_freq: List[Union[int, None]]
    neutral_values_freq: List[Union[int, None]]
    negative_values_freq: List[Union[int, None]]
    labels_mean: List[str]
    positive_values_mean: List[Union[float, None]]
    neutral_values_mean: List[Union[float, None]]
    negative_values_mean: List[Union[float, None]]
    
class GaugeChartResponse(BaseModel):
    value: float
    
    
class IssueInquiryFreqByProdcutsResponse(BaseModel):
    product_labels: List[str]
    issue_freq: List[int]
    inquiry_freq: List[int]
    best_product: str
    worst_product: str

class IssueInquiryFreqByTypeResponse(BaseModel):
    issue_type_labels: List[str]
    issue_type_frequencies: List[int]
    inquiry_type_labels: List[str]
    inquiry_type_frequencies: List[int]
    
class IssuesByEfficiencyEffectivenessResponse(BaseModel):
    effectiveness_categories: List[str]
    effectiveness_frequencies: List[int]
    efficiency_categories: List[str]
    efficiency_frequencies: List[int]
    
class InquiriesByEfficiencyEffectivenessResponse(BaseModel):
    effectiveness_categories: List[str]
    effectiveness_frequencies: List[int]
    efficiency_categories: List[str]
    efficiency_frequencies: List[int]
    
class OverallyEfficiencyEffectivenessPecentagesResponse(BaseModel):
    effectiveness_categories: List[str]
    effectiveness_percentages: List[float]
    efficiency_categories: List[str]
    efficiency_percentages: List[float]
    
class OngoingAndClosedStatsResponse(BaseModel):
    count_total_closed_issues: int 
    count_total_ongoing_issues: int
    count_total_closed_inquiries: int 
    count_total_ongoing_inquiries: int
    ongoing_percentage: float 
    closed_percentage: float
    ongoing_percentage_issues: float 
    closed_percentage_issues: float
    ongoing_percentage_inquiry: float 
    closed_percentage_inquiry: float
    
    
class BestPerformingEmailAccResponse(BaseModel):    
    best_performing_email_acc: str
    
class EmailAccEfficiencyResponse(BaseModel):  
    
    all_reading_email_accs: List[str] 
    ineff_percentages: List[float]
    less_eff_percentages: List[float] 
    mod_eff_percentages: List[float] 
    highly_eff_percentages: List[float]
    
    
class OverdueIssuesResponse(BaseModel):  
    
    sum_overdue_issues:int 
    all_reading_email_accs: List[str]
    overdue_issues_count_per_each_email: List[int] 
    total_ongoing_issues: int  
    

class TimeDataResponse(BaseModel):
    # emailLoad: List[int]
    firstResponseTimes: List[float]
    overdueCount: int
    avgFirstResponseTime: float # in minutes
    # labels: List[str]
    clientMsgTimes: List[datetime]

    
    

    
    
    
    
    
    
    
    
