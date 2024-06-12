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
 
    
   
    result = services.get_current_overall_sentiments(intervalIndays)

    return JSONResponse(content=result)




@router.get("/dashboard/get_data_for_topic_cloud/{userId}")
async def get_data_for_topic_cloud(userId: int, intervalIndays: int):
    
    result = services.get_data_for_topic_cloud(intervalIndays)

    return JSONResponse(content=result)

@router.get("/dashboard/get_data_for_word_cloud/{userId}")
async def get_data_for_word_cloud(userId: int, intervalIndays: int):
    
    result = services.get_data_for_word_cloud(intervalIndays)

    return JSONResponse(content=result)

 
@router.get("/dashboard/get_data_for_stat_cards/{userId}")
async def get_data_for_stat_cards(userId: int, intervalIndays: int):
    
    result = services.get_data_for_stat_cards(intervalIndays)
    
    return JSONResponse(content=result)


@router.get("/dashboard/get_data_for_sentiments_by_topic/{userId}")
async def get_data_for_sentiments_by_topic(userId: int, intervalIndays: int):
    
    result = services.get_data_for_sentiments_by_topic(intervalIndays)
    return JSONResponse(content=result)


@router.get("/dashboard/get_data_for_sentiments_by_time/{userId}")
async def get_data_for_sentiments_by_time(userId: int, intervalIndays: int):
    
    result = services.get_data_for_sentiments_by_time(intervalIndays)
    
    return JSONResponse(content=result)



@router.get("/dashboard/get_data_for_sentiments_distribution_of_topics/{userId}")
async def get_data_for_sentiments_distribution_of_topics(userId: int, intervalIndays: int):
    
    
    result = services.get_data_for_sentiments_distribution_of_topics(intervalIndays)
    return JSONResponse(content=result)
            

@router.get("/dashboard/get_data_value_for_gauge_chart/{userId}")
async def get_data_value_for_gauge_chart(userId: int, intervalIndays: int):
    
    result = services.get_data_value_for_gauge_chart(intervalIndays)

    return JSONResponse(content=result)
            
@router.get("/dashboard/get_data_for_issue_and_inquiry_frequency_by_products/{userId}")
async def get_data_for_issue_and_inquiry_frequency_by_products(userId: int, intervalIndays: int):
    
    products = getProductsList()
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)
    
    product_labels=[]
    issue_freq=[]
    inquiry_freq=[]
    overall_sentiment_scores_of_topics=[]
    
    
    # Iterate over each product
    for product in products:
        
        noOfIssues_perProduct = 0
        noOfInquiries_perProduct = 0
        
        product_labels.append(product)
        
        # Query MongoDB for emails with the current topic
        count_issues = collection_issues.count_documents({
            "start_time": {"$gte": n_days_ago},
            "products": {"$in": [product]}
        })
        
                # Query MongoDB for emails with the current topic
        count_inquiries = collection_inquiries.count_documents({
            "start_time": {"$gte": n_days_ago},
            "products": {"$in": [product]}
        })

        
        noOfIssues_perProduct = count_issues
        noOfInquiries_perProduct = count_inquiries
        
        issue_freq.append(noOfIssues_perProduct)
        inquiry_freq.append(noOfInquiries_perProduct)
        
        
        #-------------------finding the best and worst product by sentiment----------------------------
        emails_with_product = collection_email_msgs.find({"time": {"$gte": n_days_ago}, "products": {"$in": [product]}})

        # find the total no of emails per each topic
        totalNoOFEmails = 0
        sentiment_sum = 0.0
        for email in emails_with_product:
            totalNoOFEmails += 1
            if totalNoOFEmails>0:
                sentiment_sum = sentiment_sum + email["our_sentiment_score"] 
        
       
        if totalNoOFEmails>0:
            
            # Store sentiment sum for the current topic
            overall_sentiment_score = sentiment_sum/totalNoOFEmails
            
            overall_sentiment_scores_of_topics.append(overall_sentiment_score)
        else:
            overall_sentiment_scores_of_topics.append(0)
    
    
    # Ensure both arrays have the same length
    if len(issue_freq) != len(overall_sentiment_scores_of_topics):
        raise ValueError("Both issue_freq and overall_sentiment_scores_of_topics must have the same length")

    # Initialize an empty list to store the summation results
    summation_result = []

    # Loop through the arrays and sum the corresponding elements
    for freq, sentiment in zip(issue_freq, overall_sentiment_scores_of_topics):
        summation_result.append(sentiment*freq-freq) 
        
    min_value = min(summation_result)
    max_value = max(summation_result)
    
    min_index = summation_result.index(min_value)
    max_index = summation_result.index(max_value)
    
    result = {"product_labels":product_labels, "issue_freq":issue_freq, "inquiry_freq":inquiry_freq, "best_product":product_labels[max_index], "worst_product":product_labels[min_index]}
    return JSONResponse(content=result)   
        
@router.get("/dashboard/get_data_for_frequency_by_issue_type_and_inquiry_types/{userId}")
async def get_data_for_frequency_by_issue_type_and_inquiry_types(userId: int, intervalIndays: int):
    
    issue_types = [
        'Order Issues', 'Billing and Payment Problems', 'Account Issues', 
        'Product or Service Complaints', 'Technical Issues', 
        'Warranty and Repair Issues', 'Subscription Problems', 
        'Return and Exchange Problems'
    ]
        
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)
    
 
    issue_type_frequencies = []
    inquiry_type_frequencies = []
    
    for issue_type in issue_types:
        
        
        count_issues = collection_issues.count_documents({
            "start_time": {"$gte": n_days_ago},
            "issue_type": issue_type
        })
        
        issue_type_frequencies.append(count_issues)
    
    inquiry_types = [
        'Product Information', 'Pricing and Discounts', 'Shipping and Delivery', 
        'Warranty and Guarantees', 'Account Information', 
        'Technical Support', 'Policies and Procedures', 
        'Payment Methods'
    ]
    
    
    for inquiry_type in inquiry_types:
        
        count_inquiries = collection_inquiries.count_documents({
            "start_time": {"$gte": n_days_ago},
            "inquiry_type": inquiry_type
        })
        
        inquiry_type_frequencies.append(count_inquiries)
    
    result = {"issue_type_labels":issue_types, "issue_type_frequencies":issue_type_frequencies, "inquiry_type_labels":inquiry_types, "inquiry_type_frequencies":inquiry_type_frequencies }
    return JSONResponse(content=result)  
        

@router.get("/dashboard/get_data_for_issue_frequency_by_efficiency_and_effectiveness/{userId}")
async def get_data_for_issue_frequency_by_efficiency_and_effectiveness(userId: int, intervalIndays: int):     
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)

    
    effectiveness_categories = ['Highly Effective', 'Moderately Effective', 'Minimally Effective', 'Ineffective']
    
    efficiency_categories = ['Highly Efficient', 'Moderately Efficient', 'Less Efficient', 'Inefficient']
    
    effectiveness_frequencies = []
    efficiency_frequencies = []
    
    for effectiveness_category in effectiveness_categories:
        
        count_issues = collection_issues.count_documents({
            "start_time": {"$gte": n_days_ago},
            "effectiveness": effectiveness_category
            })
        
        effectiveness_frequencies.append(count_issues)
        
    for efficiency_category in efficiency_categories:
        
         count_issues = collection_issues.count_documents({
            "start_time": {"$gte": n_days_ago},
            "efficiency": efficiency_category
            })       
         
         efficiency_frequencies.append(count_issues)
    
    result = {"effectiveness_categories": effectiveness_categories, "effectiveness_frequencies":effectiveness_frequencies,
              "efficiency_categories":efficiency_categories, "efficiency_frequencies":efficiency_frequencies}
    
    return JSONResponse(content=result)    


@router.get("/dashboard/get_data_for_inquiry_frequency_by_efficiency_and_effectiveness/{userId}")
async def get_data_for_inquiry_frequency_by_efficiency_and_effectiveness(userId: int, intervalIndays: int):     
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)

    
    effectiveness_categories = ['Highly Effective', 'Moderately Effective', 'Minimally Effective', 'Ineffective']
    
    efficiency_categories = ['Highly Efficient', 'Moderately Efficient', 'Less Efficient', 'Inefficient']
    
    effectiveness_frequencies = []
    efficiency_frequencies = []
    
    for effectiveness_category in effectiveness_categories:
        
        count_inquiries = collection_inquiries.count_documents({
            "start_time": {"$gte": n_days_ago},
            "effectiveness": effectiveness_category
            })
        
        effectiveness_frequencies.append(count_inquiries)
        
    for efficiency_category in efficiency_categories:
        
         count_inquiries = collection_inquiries.count_documents({
            "start_time": {"$gte": n_days_ago},
            "efficiency": efficiency_category
            })       
         
         efficiency_frequencies.append(count_inquiries)
    
    result = {"effectiveness_categories": effectiveness_categories, "effectiveness_frequencies":effectiveness_frequencies,
              "efficiency_categories":efficiency_categories, "efficiency_frequencies":efficiency_frequencies}
    
    return JSONResponse(content=result)    


@router.get("/dashboard/get_data_for_overall_efficiency_and_effectiveness_percentages/{userId}")
async def get_data_for_overall_efficiency_and_effectiveness_percentages(userId: int, intervalIndays: int):  
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)

    
    effectiveness_categories = ['Highly Effective', 'Moderately Effective', 'Minimally Effective', 'Ineffective']
    
    efficiency_categories = ['Highly Efficient', 'Moderately Efficient', 'Less Efficient', 'Inefficient']
    
    effectiveness_percentages = []
    efficiency_percentages = []
    
    count_total_closed_issues = collection_issues.count_documents({
    "start_time": {"$gte": n_days_ago},
    "status": "closed"
    })
    
    count_total_closed_inquiries = collection_inquiries.count_documents({
    "start_time": {"$gte": n_days_ago},
    "status": "closed"
    })
    
    count_total_issues_and_inquiries = count_total_closed_issues+count_total_closed_inquiries
    
    if count_total_issues_and_inquiries > 0:
        
        #--------------------efficiency-----------------------------------------------------------------------------------------
        
        for efficiency_category in efficiency_categories:
            
            count_issues_per_efficiency_category = collection_issues.count_documents({
            "start_time": {"$gte": n_days_ago},
            "efficiency": efficiency_category
            }) 
            
            count_inquiries_per_efficiency_category = collection_inquiries.count_documents({
            "start_time": {"$gte": n_days_ago},
            "efficiency": efficiency_category
            })   
            
            count_total_per_efficiency_category =  count_issues_per_efficiency_category + count_inquiries_per_efficiency_category
            
            percentage_per_efficiency_category =  (count_total_per_efficiency_category/ count_total_issues_and_inquiries)*100
            
            efficiency_percentages.append(percentage_per_efficiency_category) 

        #--------------------effectiveness-----------------------------------------------------------------------------------------
        
        for effectiveness_category in effectiveness_categories:
            
            count_issues_per_effectiveness_category = collection_issues.count_documents({
            "start_time": {"$gte": n_days_ago},
            "effectiveness": effectiveness_category
            }) 
            
            count_inquiries_per_effectiveness_category = collection_inquiries.count_documents({
            "start_time": {"$gte": n_days_ago},
            "effectiveness": effectiveness_category
            })   
            
            count_total_per_effectiveness_category =  count_issues_per_effectiveness_category + count_inquiries_per_effectiveness_category
            
            percentage_per_effectiveness_category =  (count_total_per_effectiveness_category/ count_total_issues_and_inquiries)*100
            
            effectiveness_percentages.append(percentage_per_effectiveness_category) 
    else:
        effectiveness_percentages = [0,0,0,0]
        efficiency_percentages = [0,0,0,0]
        
    result = {"efficiency_categories":efficiency_categories, "efficiency_percentages":efficiency_percentages,
              "effectiveness_categories":effectiveness_categories, "effectiveness_percentages":effectiveness_percentages}
    
    return JSONResponse(content=result)
            
@router.get("/dashboard/get_data_for_ongoing_and_closed_stats/{userId}")
async def get_data_for_ongoing_and_closed_stats(userId: int, intervalIndays: int):
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)
    
    count_total_closed_issues = collection_issues.count_documents({
    "start_time": {"$gte": n_days_ago},
    "status": "closed"
    })
    
    count_total_ongoing_issues = collection_issues.count_documents({
    "start_time": {"$gte": n_days_ago},
    "status": "ongoing"
    })
    
    
    count_total_closed_inquiries = collection_inquiries.count_documents({
    "start_time": {"$gte": n_days_ago},
    "status": "closed"
    })
    
    count_total_ongoing_inquiries = collection_inquiries.count_documents({
    "start_time": {"$gte": n_days_ago},
    "status": "ongoing"
    })
    
    total_count = count_total_closed_issues + count_total_ongoing_issues + count_total_closed_inquiries + count_total_ongoing_inquiries
    total_closed_count = count_total_closed_issues + count_total_closed_inquiries
    total_ongoing_count = count_total_ongoing_issues + count_total_ongoing_inquiries
    
    if total_count>0:
        
        ongoing_percentage = (total_ongoing_count/total_count)*100
        closed_percentage = (total_closed_count/total_count)*100
    else:
        ongoing_percentage = 0
        closed_percentage = 0
        
    #--------------------- the rest is provided in case if it's needed, when I upgrade the front end to filter the donut graph by issues and inquiry.--------------------------
    
    total_issues_count = count_total_closed_issues + count_total_ongoing_issues
    total_inquiries_count = count_total_closed_inquiries + count_total_ongoing_inquiries
    
    ongoing_percentage_inquiry = 0
    closed_percentage_inquiry = 0
    ongoing_percentage_issues = 0
    closed_percentage_issues = 0
    
    if total_issues_count>0:
        ongoing_percentage_issues = (count_total_ongoing_issues/total_issues_count)*100
        closed_percentage_issues = (count_total_closed_issues/total_issues_count)*100
    
    if total_inquiries_count>0:
        ongoing_percentage_inquiry = (count_total_ongoing_inquiries/total_inquiries_count)*100
        closed_percentage_inquiry = (count_total_closed_inquiries/total_inquiries_count)*100
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------    
    result = {"count_total_closed_issues":count_total_closed_issues, "count_total_ongoing_issues":count_total_ongoing_issues,
              "count_total_closed_inquiries":count_total_closed_inquiries, "count_total_ongoing_inquiries":count_total_ongoing_inquiries,
              "ongoing_percentage":ongoing_percentage, "closed_percentage":closed_percentage,
              "ongoing_percentage_issues":ongoing_percentage_issues, "closed_percentage_issues":closed_percentage_issues,
              "ongoing_percentage_inquiry":ongoing_percentage_inquiry, "closed_percentage_inquiry":closed_percentage_inquiry}
    
    return JSONResponse(content=result)         

@router.get("/dashboard/get_data_for_best_performing_email_acc/{userId}")
async def get_data_for_best_performing_email_acc(userId: int, intervalIndays: int):
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)
    
    documents = collection_readingEmailAccounts.find({}, {"_id": 0, "address": 1})
    
    all_reading_email_accs = [doc["address"] for doc in documents]
    
    scores_for_emails = {}
    
    for reading_email_acc in all_reading_email_accs: 
        
        #------------------------------------finding the first part score - out of 40 ----------------------------------------------------------------------------------------------
        
        count_total_inquiries = collection_inquiries.count_documents({
        "start_time": {"$gte": n_days_ago},
        "recepient_email": reading_email_acc
        })
        
        count_total_issues = collection_issues.count_documents({
        "start_time": {"$gte": n_days_ago},
        "recepient_email": reading_email_acc
        })
        
        count_total_closed_inquiries = collection_inquiries.count_documents({
        "start_time": {"$gte": n_days_ago},
        "recepient_email": reading_email_acc,
        "status":"closed"
        })
        
        count_total_closed_issues = collection_issues.count_documents({
        "start_time": {"$gte": n_days_ago},
        "recepient_email": reading_email_acc,
        "status":"closed"
        })
        
        total_closed = (count_total_closed_inquiries+count_total_closed_issues) 
        first_part_score = (total_closed/(count_total_issues+count_total_inquiries))*40
        
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #------------------------------------finding the second part score - out of 60 ----------------------------------------------------------------------------------------------

        max_denominator_score = total_closed *2
        
        count_total_closed_highly_eff_issues = get_total_count_of_issues_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Highly Efficient")
        count_total_closed_moderately_eff_issues = get_total_count_of_issues_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Moderately Efficient")
        count_total_closed_less_eff_issues = get_total_count_of_issues_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Less Efficient")
        count_total_closed_ineff_issues = get_total_count_of_issues_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Inefficient")
 
        count_total_closed_highly_eff_inquiries = get_total_count_of_inquiry_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Highly Efficient")
        count_total_closed_moderately_eff_inquiries = get_total_count_of_inquiry_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Moderately Efficient")
        count_total_closed_less_eff_inquiries = get_total_count_of_inquiry_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Less Efficient")
        count_total_closed_ineff_inquiries = get_total_count_of_inquiry_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Inefficient")       
        
        count_total_closed_highly_eff = count_total_closed_highly_eff_issues + count_total_closed_highly_eff_inquiries
        count_total_closed_moderately_eff = count_total_closed_moderately_eff_issues + count_total_closed_moderately_eff_inquiries
        count_total_closed_less_eff = count_total_closed_less_eff_issues + count_total_closed_less_eff_inquiries
        count_total_closed_ineff = count_total_closed_ineff_issues + count_total_closed_ineff_inquiries
        
        numerator_score = count_total_closed_highly_eff*2 + count_total_closed_moderately_eff*1 +  count_total_closed_less_eff*0 + count_total_closed_ineff*(-1)
        
        second_part_score = (numerator_score/max_denominator_score)*60
        
        final_score_for_email_acc = first_part_score + second_part_score
        
        scores_for_emails[f"{reading_email_acc}"] = final_score_for_email_acc
        
    best_performing_email_acc = max(scores_for_emails, key=scores_for_emails.get)
    
    result = {"best_performing_email_acc":best_performing_email_acc}
    
    return JSONResponse(content=result)
        
        
@router.get("/dashboard/get_data_for_efficiency_by_email_acc/{userId}")
async def get_data_for_efficiency_by_email_acc(userId: int, intervalIndays: int):  
     
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)
    
    documents = collection_readingEmailAccounts.find({}, {"_id": 0, "address": 1})
    
    all_reading_email_accs = [doc["address"] for doc in documents]
    
    highly_eff_percentages = []
    mod_eff_percentages = []
    less_eff_percentages = []
    ineff_percentages = []
    
    for reading_email_acc in all_reading_email_accs:
        
        no_of_highly_eff_issues = get_total_count_of_issues_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Highly Efficient")
        no_of_mod_eff_issues = get_total_count_of_issues_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Moderately Efficient")
        no_of_less_eff_issues = get_total_count_of_issues_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Less Efficient")
        no_of_ineff_issues = get_total_count_of_issues_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Inefficient")

        no_of_highly_eff_inquiries = get_total_count_of_inquiry_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Highly Efficient")
        no_of_mod_eff_inquiries = get_total_count_of_inquiry_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Moderately Efficient")
        no_of_less_eff_inquiries = get_total_count_of_inquiry_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Less Efficient")
        no_of_ineff_inquiries = get_total_count_of_inquiry_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, "Inefficient")
        
        total_closed_issues = no_of_highly_eff_issues+no_of_mod_eff_issues+no_of_less_eff_issues+no_of_ineff_issues
        total_closed_inquiries = no_of_highly_eff_inquiries+no_of_mod_eff_inquiries+no_of_less_eff_inquiries+no_of_ineff_inquiries
        
        total_closed = total_closed_issues+total_closed_inquiries
        
        if total_closed>0:
            highly_eff_percentage = ((no_of_highly_eff_issues+no_of_highly_eff_inquiries)/total_closed)*100
            highly_eff_percentages.append(highly_eff_percentage)
            
            mod_eff_percentage = ((no_of_mod_eff_issues+no_of_mod_eff_inquiries)/total_closed)*100
            mod_eff_percentages.append(mod_eff_percentage)
            
            less_eff_percentage = ((no_of_less_eff_issues+no_of_less_eff_inquiries)/total_closed)*100
            less_eff_percentages.append(less_eff_percentage)
            
            ineff_percentage = ((no_of_ineff_issues+no_of_ineff_inquiries)/total_closed)*100
            ineff_percentages.append(ineff_percentage)
        else:
            highly_eff_percentages.append(0)
            mod_eff_percentages.append(0)
            less_eff_percentages.append(0)
            ineff_percentages.append(0)
    
    result = {"all_reading_email_accs":all_reading_email_accs, "ineff_percentages":ineff_percentages, 
              "less_eff_percentages":less_eff_percentages, "mod_eff_percentages":mod_eff_percentages, 
              "highly_eff_percentages":highly_eff_percentages}
    return JSONResponse(content=result)
            

@router.get("/dashboard/get_data_for_overdue_issues/{userId}")
async def get_data_for_overdue_issues(userId: int, intervalIndays: int):           

    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)
    
    documents = collection_readingEmailAccounts.find({}, {"_id": 0, "address": 1})
    
    all_reading_email_accs = [doc["address"] for doc in documents]
    
    sum_overdue_issues = 0
    
    overdue_issue_count_of_each_email = []
    
    for reading_email_acc in all_reading_email_accs: 
        
        #------------------------------------finding the first part score - out of 40 ----------------------------------------------------------------------------------------------
        
        count_overdue_issues_per_email_acc = collection_issues.count_documents({
        "start_time": {"$gte": n_days_ago},
        "recepient_email": reading_email_acc,
        "status":"ongoing",
        "isOverdue": True
        }) 
        
        overdue_issue_count_of_each_email.append(count_overdue_issues_per_email_acc)
        
        sum_overdue_issues = sum_overdue_issues + count_overdue_issues_per_email_acc
    
        total_ongoing_issues = collection_issues.count_documents({
        "start_time": {"$gte": n_days_ago},
        "status": "ongoing"
        }) 
        
    result = {"sum_overdue_issues":sum_overdue_issues, "all reading_email_accs": all_reading_email_accs,
              "overdue_issues_count_per_each_email":overdue_issue_count_of_each_email, 
              "total_ongoing_issues":total_ongoing_issues}
    
    return JSONResponse(content=result)          
        

#-------------------------------------------------------helper functions--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_total_count_of_issues_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, efficiency_category ):
    
    count_total_closed_certain_eff_issues = collection_issues.count_documents({
        "start_time": {"$gte": n_days_ago},
        "recepient_email": reading_email_acc,
        "status":"closed",
        "efficiency":efficiency_category
        })
    
    return count_total_closed_certain_eff_issues

def get_total_count_of_inquiry_for_certain_efficiency_and_certain_recepient(n_days_ago, reading_email_acc, efficiency_category ):
    
    count_total_closed_certain_eff_inquiry = collection_inquiries.count_documents({
        "start_time": {"$gte": n_days_ago},
        "recepient_email": reading_email_acc,
        "status":"closed",
        "efficiency":efficiency_category
        })
    
    return count_total_closed_certain_eff_inquiry


# generate colors for the sentiments by topic bar chart
def generateRandomColorForBarChart(score):

        
    if score>=-0.3 and score<=0.3:
        
        if score>=-0.15 and score<=0.15:
        
            red = random.randint(200, 225)
            green = random.randint(200, 225)
            blue = random.randint(0, 150)
        else:
            red = random.randint(225, 255)
            green = random.randint(225, 255)
            blue = random.randint(0, 150)  
             

        
    elif score>0.3:
        if score>0.6:
            red = random.randint(0, 255)
            green = random.randint(225, 255)
            blue = random.randint(0, 255)
        else:
            red = random.randint(0, 255)
            green = random.randint(200, 255)
            blue = random.randint(0, 255)
        
    elif score<-0.3:
        if score<-0.6:
            red = random.randint(225, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)
        else:
            red = random.randint(200, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)        
    
           
    color = f'rgba({red}, {green}, {blue}, 0.9)'  
    return color



def generateRandomColor():
    
    # generate random color 
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    
    color = f'rgba({red}, {green}, {blue}, 0.9)' 
    
    return color



