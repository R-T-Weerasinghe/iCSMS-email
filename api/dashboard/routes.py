from datetime import datetime, timedelta, timezone
import random
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from api.email_filtering_and_info_generation.configurations.database import collection_notificationSendingChannels,collection_email_msgs


router = APIRouter()


# send current reading emails to frontend   
@router.get("/dashboard/get_current_overall_sentiments/{user_id}")
async def get_current_overall_sentiments(user_id: int):
 
    
   
    recipients = ["raninduharischandra12@gmail.com", "harischandrahbr.21@uom.lk"]
    
    # Query MongoDB for documents matching recipients
    query = {"recipient": {"$in": recipients}}
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

        return JSONResponse(content=result)
    else:
        return JSONResponse(content={})



@router.get("/dashboard/get_data_for_topic_cloud/{userId}")
async def get_data_for_topic_cloud(userId: int):
    
    # change this so to get the topics list from the DB
    topics = ['business','products', 'marketing issues', 'assignments', 'education', 'UN', 'AI']

    # Initialize a dictionary to store topic frequencies
    topic_frequencies = {topic: 0 for topic in topics}

    # Query MongoDB to retrieve documents
    cursor = collection_email_msgs.find()

    # Iterate over each document
    for document in cursor:
        # Extract the topics array from the document
        document_topics = document.get("topics", [])

        # Count the frequency of each topic
        for topic in document_topics:
            if topic in topics:
                topic_frequencies[topic] += 1

    # Convert the dictionary to a list of dictionaries with topic and frequency
    result = [{"topic": topic, "frequency": frequency} for topic, frequency in topic_frequencies.items()]

    return JSONResponse(content=result)

 
@router.get("/dashboard/get_data_for_stat_cards/{userId}")
async def get_data_for_stat_cards(userId: int):
    
    recepient_emails = [{"id":1, "address":"harischandrahbr.21@uom.lk", "nickname":"haris1"},{"id":2, "address":"raninduharischandra12@gmail.com", "nickname":"ranindu"}]
    # {"id":3, "address":"'R-T-Weerasinghe/iCSMS-email' <iCSMS-email@noreply.github.com>", "nickname":"rav1"}
    evenCounter = 0
    result = []
    for recepient_email in recepient_emails:
        query = {"recipient": recepient_email["address"]}
        cursor = collection_email_msgs.find(query)
        
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
    
    return JSONResponse(content=result)


@router.get("/dashboard/get_data_for_sentiments_by_topic/{userId}")
async def get_data_for_sentiments_by_topic(userId: int):
    
    topics = ['business','products', 'marketing issues', 'assignments', 'education', 'UN', 'AI']
    
    # Initialize dictionary to store sentiment sums for each topic
    overall_sentiment_scores = []
    colors = []
    found_topics = []

    # Iterate over each topic
    for topic in topics:
 
        # Query MongoDB for emails with the current topic
        emails_with_topic = collection_email_msgs.find({"topics": {"$in": [topic]}})

        # find the total no of emails per each topic
        totalNoOFEmails = 0
        sentiment_sum = 0.0
        for email in emails_with_topic:
            totalNoOFEmails += 1
            if totalNoOFEmails>0:
                sentiment_sum = sentiment_sum + email["our_sentiment_score"] 
        
       
        if totalNoOFEmails>0:
            
            # Store sentiment sum for the current topic
            overall_sentiment_score = sentiment_sum/totalNoOFEmails
            
            color = generateRandomColor(overall_sentiment_score)
            
            while color in colors:
                color = generateRandomColor(overall_sentiment_score)
            
            found_topics.append(topic)
            overall_sentiment_scores.append(overall_sentiment_score)
            colors.append(color)
            
       
            
            
    result = {"sbtChartLabels":found_topics, "sbtChartColors": colors, "sbtChartValues": overall_sentiment_scores}
    return JSONResponse(content=result)


# generate colors for the sentiments by topic bar chart
def generateRandomColor(score):

        
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



@router.get("/dashboard/get_data_for_sentiments_by_time/{userId}")
async def get_data_for_sentiments_by_time(userId: int):
    
    labels = []
    positive_values = []
    neutral_values = []    
    negative_values = []
    
    # currently making for the past 3 days + today
    numberOfDaysToThePast = 3
    
    # get current time
    current_time = datetime.now(timezone.utc)

    
    formatted_current_time = current_time.strftime("%d %b")
 
    
    delayday = numberOfDaysToThePast
    
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
            positive_values.append(overall_postiive_sum_for_the_day/total_no_of_positives)
        else:
            positive_values.append(None)
        
        if total_no_of_neutrals>0:
            neutral_values.append(overall_neutral_sum_for_the_day/total_no_of_neutrals)
        else:
            neutral_values.append(None)  
                 
        if total_no_of_negatives>0:
            negative_values.append(overall_negative_sum_for_the_day/total_no_of_negatives)
        else:
            negative_values.append(None)            
            
        delayday -= 1
    
    result = {"labels": labels, "positive_values":positive_values, "neutral_values":neutral_values, "negative_values":negative_values}
    
    return JSONResponse(content=result)