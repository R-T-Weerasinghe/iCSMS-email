from typing import List
from fastapi import HTTPException
from api.dashboard.models import BestPerformingEmailAccResponse, EmailAccEfficiencyResponse, GaugeChartResponse, InquiriesByEfficiencyEffectivenessResponse, IssueInquiryFreqByProdcutsResponse, IssueInquiryFreqByTypeResponse, IssuesByEfficiencyEffectivenessResponse, OngoingAndClosedStatsResponse, OverallyEfficiencyEffectivenessPecentagesResponse, OverdueIssuesResponse, SentimentsByTimeResponse, SentimentsByTopicResponse, SentimentsDistributionByTimeResponse, GetCurrentOverallSentimentProgress, StatCardSingleResponse, WordCloudSingleResponse
from api.email_filtering_and_info_generation.configurations.database import collection_notificationSendingChannels,collection_email_msgs,collection_inquiries,collection_issues, collection_readingEmailAccounts, collection_configurations
from datetime import datetime, timedelta, timezone
import random

from api.email_filtering_and_info_generation.schemas import list_readingEmailAcc_serial


async def get_current_overall_sentiments( intervalIndays: int):
 
    
   
    recipients = await get_all_reading_email_accounts()
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)
    
    # Query MongoDB for documents matching recipients
    query = {"recipient": {"$in": recipients}, "time": {"$gte": n_days_ago}}
    results = collection_email_msgs.find(query, {"_id": 0, "our_sentiment_score": 1})
    
    # Extract our_sentiment_score values
    sentiment_scores = [doc["our_sentiment_score"] for doc in results]
    print(sentiment_scores)
    
    total_frequency= len(sentiment_scores)
    
    if total_frequency != 0:
        positive_frequency= 0
        neutral_frequency= 0
        negative_frequency= 0
        
        for score in sentiment_scores:
            if score>=-0.3 and score<=0.3:
                print("neutral", score)
                neutral_frequency +=1
            elif score>0.3:
                print("positive", score)
                positive_frequency +=1
            else:
               
                negative_frequency +=1
        
        positive_percentage = (positive_frequency/total_frequency)*100
        neutral_percentage = (neutral_frequency/total_frequency)*100
        negative_perecentage = (negative_frequency/total_frequency)*100
        
        print()
        
        result =  GetCurrentOverallSentimentProgress(positive_percentage= positive_percentage, 
                                                          neutral_percentage= neutral_percentage, 
                                                          negative_percentage= negative_perecentage)
        
        return result
    else:
        return GetCurrentOverallSentimentProgress(positive_percentage= 0, 
                                                          neutral_percentage= 0, 
                                                          negative_percentage= 0)
            
    
    
async def get_data_for_topic_cloud(intervalIndays: int):
    
    # change this so to get the topics list from the DB
    products = getProductsList()
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)

    # Initialize a dictionary to store topic frequencies
    products_frequencies = {product: 0 for product in products}

    # Query MongoDB to retrieve documents
    cursor = collection_email_msgs.find({"time": {"$gte": n_days_ago}})

    # Iterate over each document
    for document in cursor:
        # Extract the topics array from the document
        document_products = document.get("products", [])

        # Count the frequency of each topic
        for product in document_products:
            if product in products:
                products_frequencies[product] += 1

    # Convert the dictionary to a list of dictionaries with topic and frequency
    result = [{"product": product, "frequency": frequency} for product, frequency in products_frequencies.items()]    
    
    return result




async def get_data_for_word_cloud(intervalIndays: int):
    
    # change this so to get the topics list from the DB
    topics = getProductsList()
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)

    # Initialize a dictionary to store topic frequencies
    topic_frequencies = {topic: 0 for topic in topics}

    # Query MongoDB to retrieve documents
    cursor = collection_email_msgs.find({"time": {"$gte": n_days_ago}})

    # Iterate over each document
    for document in cursor:
        # Extract the topics array from the document
        document_topics = document.get("topics", [])

        # Count the frequency of each topic
        for topic in document_topics:
            if topic in topics:
                topic_frequencies[topic] += 1
    

    
    # Convert the dictionary to a list of dictionaries with topic and frequency
    result = [WordCloudSingleResponse(topic= topic, frequency= frequency, color= generateRandomColor()) for topic, frequency in topic_frequencies.items()]
    
    return result
    


async def get_data_for_stat_cards(intervalIndays: int):
    
    recepient_emails = get_reading_emails_array()
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)
    
    evenCounter = 0
    result: List[StatCardSingleResponse] = []
    for recepient_email in recepient_emails:
        query = {"recipient": recepient_email["address"]}
        cursor = collection_email_msgs.find({"time": {"$gte": n_days_ago}}, query)
        
        if cursor:
            
            overall_sentiment_score_sum = 0
            total_emails = 0
            
            for document in cursor:
                total_emails += 1

            if total_emails == 0:
                raise HTTPException(status_code=404, detail="Recipient not found")

            for document in cursor:
                overall_sentiment_score_sum = overall_sentiment_score_sum + document["our_sentiment_score"]
                
            sentiement_score = overall_sentiment_score_sum/total_emails
            
            sentiment = ""
            if sentiement_score>=-0.3 and sentiement_score<=0.3:
                sentiment = "Neutral"
            elif sentiement_score>0.3:
                sentiment = "Positive"
            else:
                sentiment = "Negative"
            
            imgPath = ""
            evenCounter += 1
            if evenCounter%2 == 1:
                imgPath = "./email/mail_blue.png"
            else:
                imgPath = "./email/mail_red.png"
                
            result.append(StatCardSingleResponse(title= total_emails, 
                                                    sub_title= "Total Emails", 
                                                    header= recepient_email["nickname"], 
                                                    sentiment= sentiment, 
                                                    imgPath= imgPath))

    return result


async def get_data_for_sentiments_by_topic(intervalIndays: int):
    
    products = getProductsList()
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)
    
    # Initialize dictionary to store sentiment sums for each topic
    overall_sentiment_scores = []
    colors = []
    found_products = []

    # Iterate over each topic
    for product in products:
 
        # Query MongoDB for emails with the current topic
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
            
            color = generateRandomColorForBarChart(overall_sentiment_score)
            
            while color in colors:
                color = generateRandomColorForBarChart(overall_sentiment_score)
            
            found_products.append(product)
            overall_sentiment_scores.append(overall_sentiment_score)
            colors.append(color)
            
       
            
            
    result = SentimentsByTopicResponse(sbtChartLabels=found_products, 
                                          sbtChartColors= colors, 
                                          sbtChartValues= overall_sentiment_scores)
    
    return result


async def get_data_for_sentiments_by_time(intervalIndays: int):
    
    labels = []
    positive_values = []
    neutral_values = []    
    negative_values = []
    
    
    # get current time
    current_time = datetime.now(timezone.utc)

    
    formatted_current_time = current_time.strftime("%d %b")
 
    
    delayday = intervalIndays
    
    while(delayday>=0):
        
        """
        delayday = 0 = today
        delayday = 1 = yesterday
        delayday = 2 = day before yesterday
        delayday = 3 = two days before yesterday """
        
        # Get checking day date
        checking_day = current_time - timedelta(days=delayday)
        formatted_checking_day = checking_day.strftime("%d %b")
  
        
        
        overall_postiive_sum_for_the_day = 0
        overall_neutral_sum_for_the_day = 0
        overall_negative_sum_for_the_day = 0
        
        total_no_of_positives = 0
        total_no_of_negatives = 0    
        total_no_of_neutrals = 0
        
        

        # Query to find emails that arrived in the checking day
        query = {"time": {"$gte": checking_day.replace(hour=0, minute=0, second=0, microsecond=0),
                        "$lt": checking_day.replace(hour=23, minute=59, second=59, microsecond=999999)}}

        # Retrieve emails
        checkingday_emails = collection_email_msgs.find(query)
        
        if checkingday_emails != []:
            
            labels.append(formatted_checking_day)
            
            #  add the respective  sentiments values to their respective lists
            for email in checkingday_emails:
                sentiment_score = email["our_sentiment_score"]
                
                if sentiment_score>=-0.3 and sentiment_score<=0.3:
                    
                   overall_neutral_sum_for_the_day = overall_neutral_sum_for_the_day + sentiment_score
                   total_no_of_neutrals += 1
                   
                elif sentiment_score>0.3:
                   overall_postiive_sum_for_the_day = overall_postiive_sum_for_the_day + sentiment_score
                   total_no_of_positives += 1
                else:
                   overall_negative_sum_for_the_day = overall_negative_sum_for_the_day + sentiment_score
                   total_no_of_negatives += 1
                   
        if total_no_of_positives>0:       
            positive_values.append(round(overall_postiive_sum_for_the_day/total_no_of_positives,2))
        else:
            positive_values.append(None)
        
        if total_no_of_neutrals>0:
            neutral_values.append(round(overall_neutral_sum_for_the_day/total_no_of_neutrals,2))
        else:
            neutral_values.append(None)  
                 
        if total_no_of_negatives>0:
            negative_values.append(round(overall_negative_sum_for_the_day/total_no_of_negatives,2))
        else:
            negative_values.append(None)            
            
        delayday -= 1
    
    result = SentimentsByTimeResponse(labels= labels, 
              positive_values= positive_values, 
              neutral_values= neutral_values, 
              negative_values= negative_values)
    
    return result

async def get_data_for_sentiments_distribution_of_topics(intervalIndays: int):
    
    products = getProductsList()
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)
    
    labels_freq=[]
    positive_values_freq=[]
    neutral_values_freq=[]
    negative_values_freq=[]
    
    labels_mean=[]
    positive_values_mean=[]
    neutral_values_mean=[]
    negative_values_mean=[]
    
    # Iterate over each product
    for product in products:
        
        noOfPositiveEmails_perTopic = 0
        noOfNeutralEmails_perTopic = 0
        noOfNegativeEmails_perTopic = 0
        
        labels_freq.append(product)
        
        # Query MongoDB for emails with the current topic
        emails_with_product = collection_email_msgs.find({"time": {"$gte": n_days_ago}, "products": {"$in": [product]}}, {"_id": 0, "our_sentiment_score": 1})

        
        if emails_with_product!= []:
                       
            positiveSentimentSum_ofTopic = 0
            neutralSentimentSum_ofTopic = 0
            negativeSentimentSum_ofTopic = 0
            
            labels_mean.append(product)
            
            for email in emails_with_product:
                
                sentiment_score = email["our_sentiment_score"] 
                
                if sentiment_score>=-0.3 and sentiment_score<=0.3:
                    noOfNeutralEmails_perTopic += 1
                    neutralSentimentSum_ofTopic = neutralSentimentSum_ofTopic + sentiment_score
                elif sentiment_score>0.3:
                    noOfPositiveEmails_perTopic += 1
                    positiveSentimentSum_ofTopic = positiveSentimentSum_ofTopic + sentiment_score
                else:
                    noOfNegativeEmails_perTopic += 1
                    negativeSentimentSum_ofTopic = negativeSentimentSum_ofTopic + sentiment_score
            
            if noOfPositiveEmails_perTopic>0:
                positive_values_mean.append(positiveSentimentSum_ofTopic/noOfPositiveEmails_perTopic)
            else:
                positive_values_mean.append(None)
                
            if noOfNeutralEmails_perTopic>0:
                neutral_values_mean.append(neutralSentimentSum_ofTopic/noOfNeutralEmails_perTopic)
            else:
                neutral_values_mean.append(None)
                
            if noOfNegativeEmails_perTopic>0:
                negative_values_mean.append(negativeSentimentSum_ofTopic/noOfNegativeEmails_perTopic)
            else:
                negative_values_mean.append(None)
                
            positive_values_freq.append(noOfPositiveEmails_perTopic)
            neutral_values_freq.append(noOfNeutralEmails_perTopic)
            negative_values_freq.append(noOfNegativeEmails_perTopic)

        else:
            
            positive_values_freq.append(0)
            neutral_values_freq.append(0)
            negative_values_freq.append(0)
            
    result = SentimentsDistributionByTimeResponse(
              labels_freq= labels_freq, 
              positive_values_freq = positive_values_freq, 
              neutral_values_freq = neutral_values_freq, 
              negative_values_freq = negative_values_freq,
              labels_mean = labels_mean, 
              positive_values_mean = positive_values_mean, 
              neutral_values_mean = neutral_values_mean, 
              negative_values_mean = negative_values_mean)

    return result


async def get_data_value_for_gauge_chart(intervalIndays: int):
    # Calculate the date n days ago
    print(intervalIndays)
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)

    # Query MongoDB collection for emails within the past n days for the given userId
    emails = collection_email_msgs.find({"time": {"$gte": n_days_ago}})
    
    
        
    total_sentiment_score = 0
    no_of_emails = 0
    
    for email in emails:
        no_of_emails += 1
        total_sentiment_score = total_sentiment_score + email["our_sentiment_score"]
    
    print("total_sentiment_score", total_sentiment_score, "no_of_emails", no_of_emails)
    
    if no_of_emails>0:
        avg_sentiment_score = round(total_sentiment_score/no_of_emails,3)
        
        result = GaugeChartResponse(value= avg_sentiment_score)
        print("gauge chart value",result)
       
    
    else:
        
        result = GaugeChartResponse(value= 0)
        
    return result


async def get_data_for_issue_and_inquiry_frequency_by_products(intervalIndays: int):
    
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
    
    result = IssueInquiryFreqByProdcutsResponse(
              product_labels = product_labels, 
              issue_freq = issue_freq, 
              inquiry_freq = inquiry_freq, 
              best_product = product_labels[max_index], 
              worst_product = product_labels[min_index])
    
    return result

async def get_data_for_frequency_by_issue_type_and_inquiry_types(intervalIndays: int):
    
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
    
    result = IssueInquiryFreqByTypeResponse(
               issue_type_labels=issue_types, 
              issue_type_frequencies = issue_type_frequencies, 
              inquiry_type_labels = inquiry_types, 
              inquiry_type_frequencies = inquiry_type_frequencies )
    return result


async def get_data_for_issue_frequency_by_efficiency_and_effectiveness(intervalIndays: int):     
    
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
    
    result = IssuesByEfficiencyEffectivenessResponse(
              effectiveness_categories = effectiveness_categories, 
              effectiveness_frequencies = effectiveness_frequencies,
              efficiency_categories = efficiency_categories, 
              efficiency_frequencies = efficiency_frequencies)
    
    return result
    
async def get_data_for_inquiry_frequency_by_efficiency_and_effectiveness(intervalIndays: int):     
    
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
    
    result = InquiriesByEfficiencyEffectivenessResponse(
              effectiveness_categories = effectiveness_categories, 
              effectiveness_frequencies = effectiveness_frequencies,
              efficiency_categories = efficiency_categories, 
              efficiency_frequencies = efficiency_frequencies)
    
    return result    
    
    
async def get_data_for_overall_efficiency_and_effectiveness_percentages(intervalIndays: int):  
    
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
        
    result = OverallyEfficiencyEffectivenessPecentagesResponse(
              effectiveness_categories = effectiveness_categories, 
              effectiveness_percentages = effectiveness_percentages,
              efficiency_categories = efficiency_categories, 
              efficiency_percentages = efficiency_percentages
              )
    
    return result  
    
async def get_data_for_ongoing_and_closed_stats(intervalIndays: int):
    
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
        
        ongoing_percentage: float = (total_ongoing_count/total_count)*100
        closed_percentage: float= (total_closed_count/total_count)*100
    else:
        ongoing_percentage: float = 0
        closed_percentage: float = 0
        
    #--------------------- the rest is provided in case if it's needed, when I upgrade the front end to filter the donut graph by issues and inquiry.--------------------------
    
    total_issues_count = count_total_closed_issues + count_total_ongoing_issues
    total_inquiries_count = count_total_closed_inquiries + count_total_ongoing_inquiries
    
    ongoing_percentage_inquiry: float = 0
    closed_percentage_inquiry: float = 0
    ongoing_percentage_issues: float = 0
    closed_percentage_issues: float = 0
    
    if total_issues_count>0:
        ongoing_percentage_issues = (count_total_ongoing_issues/total_issues_count)*100
        closed_percentage_issues = (count_total_closed_issues/total_issues_count)*100
    
    if total_inquiries_count>0:
        ongoing_percentage_inquiry = (count_total_ongoing_inquiries/total_inquiries_count)*100
        closed_percentage_inquiry = (count_total_closed_inquiries/total_inquiries_count)*100
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------    
    result = OngoingAndClosedStatsResponse(
              count_total_closed_issues = count_total_closed_issues, 
              count_total_ongoing_issues = count_total_ongoing_issues,
              count_total_closed_inquiries = count_total_closed_inquiries, 
              count_total_ongoing_inquiries = count_total_ongoing_inquiries,
              ongoing_percentage = ongoing_percentage, 
              closed_percentage = closed_percentage,
              ongoing_percentage_issues = ongoing_percentage_issues, 
              closed_percentage_issues = closed_percentage_issues,
              ongoing_percentage_inquiry = ongoing_percentage_inquiry, 
              closed_percentage_inquiry = closed_percentage_inquiry)
    
    return result   
    
async def get_data_for_best_performing_email_acc(intervalIndays: int):
    
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
    
    result = BestPerformingEmailAccResponse(best_performing_email_acc = best_performing_email_acc)
    
    return result   
    
async def get_data_for_efficiency_by_email_acc(intervalIndays: int):  
     
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)
    
    documents = collection_readingEmailAccounts.find({}, {"_id": 0, "address": 1})
    
    all_reading_email_accs = [doc["address"] for doc in documents]
    
    highly_eff_percentages: List[float] = []
    mod_eff_percentages: List[float] = []
    less_eff_percentages: List[float] = []
    ineff_percentages: List[float] = []
    
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
            highly_eff_percentage = (float)((no_of_highly_eff_issues+no_of_highly_eff_inquiries)/total_closed)*100
            highly_eff_percentages.append(highly_eff_percentage)
            
            mod_eff_percentage = (float)((no_of_mod_eff_issues+no_of_mod_eff_inquiries)/total_closed)*100
            mod_eff_percentages.append(mod_eff_percentage)
            
            less_eff_percentage = (float)((no_of_less_eff_issues+no_of_less_eff_inquiries)/total_closed)*100
            less_eff_percentages.append(less_eff_percentage)
            
            ineff_percentage =(float)((no_of_ineff_issues+no_of_ineff_inquiries)/total_closed)*100
            ineff_percentages.append(ineff_percentage)
        else:
            highly_eff_percentages.append(0)
            mod_eff_percentages.append(0)
            less_eff_percentages.append(0)
            ineff_percentages.append(0)
    
    result = EmailAccEfficiencyResponse(
              all_reading_email_accs = all_reading_email_accs, 
              ineff_percentages = ineff_percentages, 
              less_eff_percentages = less_eff_percentages, 
              mod_eff_percentages = mod_eff_percentages, 
              highly_eff_percentages = highly_eff_percentages)
    
    return result   

async def get_data_for_overdue_issues(intervalIndays: int):           

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
        
    result = OverdueIssuesResponse(
              sum_overdue_issues = sum_overdue_issues, 
              all_reading_email_accs = all_reading_email_accs,
              overdue_issues_count_per_each_email = overdue_issue_count_of_each_email, 
              total_ongoing_issues = total_ongoing_issues)
    
    
    return result







# -------------------------------------------helper functions--------------------------------------------------------------------    

async def get_all_reading_email_accounts():
    documents = collection_readingEmailAccounts.find({}, {"_id": 0, "address": 1})
    
    return [doc["address"] for doc in documents]


async def getProductsList():

 result = collection_configurations.find_one({"id": 1})
 if result:
    productsList = result.get("products",[])
    return productsList

 else:
    print("No document found with id 1")
    return []


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


async def get_reading_emails_array():
    email_acc_array = list_readingEmailAcc_serial(collection_readingEmailAccounts.find())
    return email_acc_array










