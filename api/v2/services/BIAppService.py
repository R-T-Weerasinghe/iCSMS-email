

from api.v2.models.BIAPPModel import BIAppResponse, ProductPeformenceScoresResponse
from api.v2.models.dashboardModel import IssueInquiryFreqByProdcutsResponse
from api.v2.services.dashboardService import get_current_overall_sentiments, get_data_for_frequency_by_issue_type_and_inquiry_types, get_data_for_issue_and_inquiry_frequency_by_products, get_data_for_overall_efficiency_and_effectiveness_percentages, getProductsList


async def generate_bi_response(intervalInDaysStart: int, intervalInDaysEnd:int):
 
    iss_inq_by_prodcuts_response:IssueInquiryFreqByProdcutsResponse = await get_data_for_issue_and_inquiry_frequency_by_products(intervalInDaysStart, intervalInDaysEnd)

    sentiment_percentages = await get_current_overall_sentiments(intervalInDaysStart, intervalInDaysEnd)
    effi_and_effec_percentages = await get_data_for_overall_efficiency_and_effectiveness_percentages(intervalInDaysStart, intervalInDaysEnd)
    
    product_performance_response = ProductPeformenceScoresResponse(
        product_labels = iss_inq_by_prodcuts_response.product_labels,
        product_performance_scores = iss_inq_by_prodcuts_response.performence_scores)
    
    best_product = iss_inq_by_prodcuts_response.best_product
    worst_product = iss_inq_by_prodcuts_response.worst_product
    
    iss_inq_type_counts = await get_data_for_frequency_by_issue_type_and_inquiry_types(intervalInDaysStart, intervalInDaysEnd)
    
    return BIAppResponse(
        sentiment_percentages = sentiment_percentages,
        effi_and_effec_percentages = effi_and_effec_percentages,
        product_performance = product_performance_response,
        best_product = best_product,
        worst_product = worst_product,
        iss_inq_type_counts = iss_inq_type_counts
        
    )
    