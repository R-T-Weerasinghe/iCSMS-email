from fastapi import HTTPException
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
        
        result =  {"positive_percentage": positive_percentage, "neutral_percentage": neutral_percentage, "negative_percentage": negative_perecentage}
        
        return result
    else:
        return {"positive_percentage": 0, "neutral_percentage": 0, "negative_percentage": 0}
            
    
    
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
    result = [{"topic": topic, "frequency": frequency, "color": generateRandomColor()} for topic, frequency in topic_frequencies.items()]
    
    return result
    


async def get_data_for_stat_cards(intervalIndays: int):
    
    recepient_emails = get_reading_emails_array()
    
    n_days_ago = datetime.utcnow() - timedelta(days=intervalIndays)
    
    evenCounter = 0
    result = []
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
                
            result.append({'title':total_emails, 'sub_title':"Total Emails", "header":recepient_email["nickname"], "sentiment": sentiment, "imgPath":imgPath})

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
            
       
            
            
    result = {"sbtChartLabels":found_products, "sbtChartColors": colors, "sbtChartValues": overall_sentiment_scores}
    
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
    
    result = {"labels": labels, "positive_values":positive_values, "neutral_values":neutral_values, "negative_values":negative_values}
    
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
            
    result = {"labels_freq": labels_freq, "positive_values_freq":positive_values_freq, 
              "neutral_values_freq":neutral_values_freq, "negative_values_freq":negative_values_freq,
              "labels_mean":labels_mean, "positive_values_mean":positive_values_mean, 
              "neutral_values_mean":neutral_values_mean, "negative_values_mean":negative_values_mean}

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
        
        result = {"value": avg_sentiment_score}
        print("gauge chart value",result)
       
    
    else:
        
        result = {"value": 0}
        
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