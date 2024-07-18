from typing import List
from pydantic import BaseModel

from api.v2.models.dashboardModel import GetCurrentOverallSentimentProgress, IssueInquiryFreqByTypeResponse, OverallyEfficiencyEffectivenessPecentagesResponse


class ProductPeformenceScoresResponse(BaseModel):
    product_labels: List[str]
    product_performance_scores:List[float]

class BIAppResponse(BaseModel):
    sentiment_percentages:GetCurrentOverallSentimentProgress
    effi_and_effec_percentages:OverallyEfficiencyEffectivenessPecentagesResponse
    product_performance:ProductPeformenceScoresResponse
    best_product: str
    worst_product: str
    iss_inq_type_counts:IssueInquiryFreqByTypeResponse
    
