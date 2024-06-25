from typing import List
import nltk

# Download the punkt package
nltk.download('punkt')


from datetime import datetime, timedelta
from api.thread_summaries_page.models import ThreadSummary, GeneralThreadSummary, ThreadSummaryResponse, AllThreadsSummaryResponse
from email_filtering_and_info_generation.configurations.database import collection_conversations


async def getHotThreads():
    
      # get the thread_id and the updated_times arr for each thread_summary
    cursor = collection_conversations.find({}, {'thread_id': 1, 'updated_times': 1})

    thread_recent_replies_arr = []

    for doc in cursor:
        thread_id = doc['thread_id']
        updated_times = doc['updated_times']
        
        now = datetime.utcnow()
        four_days_ago = now - timedelta(days=4)

        # Filter datetime objects within the last 4 days
        filtered_date_times = [dt for dt in updated_times if dt >= four_days_ago]

        # Count the number of datetime objects within the last 4 days
        count_within_last_4_days = len(filtered_date_times)
        
        thread_recent_replies_arr.append({thread_id:count_within_last_4_days})
        
        
        
        

    sorted_thread_recent_replies_arr = sorted(thread_recent_replies_arr, key=lambda x: list(x.values())[0], reverse=True)
    
    
    hot_thread_ids = []
    
    if len(sorted_thread_recent_replies_arr) > 5:
        
        hot_thread_ids = [list(d.keys())[0] for d in sorted_thread_recent_replies_arr[:5]]
    
    else:
        hot_thread_ids = [list(d.keys())[0] for d in sorted_thread_recent_replies_arr]
    
    
    hot_threads: List[ThreadSummary] = []
    total = len(hot_thread_ids)
    
    for thread_id in hot_thread_ids:
        
        doc = collection_conversations.find_one({'thread_id': thread_id})
        
        subject = doc['subject']
        last_updated_time = doc['updated_times'][-1]
        summary = doc['summary']
        
        # Tokenize the summary into sentences
        sentences = nltk.tokenize.sent_tokenize(summary)

        # Get the first few sentences 
        num_sentences = 3
        snippet = ' '.join(sentences[:num_sentences])

        tags = doc['products']
        
        single_thread_summary = ThreadSummary(
                                subject=subject, lastUpdate=last_updated_time,
                                summary=summary,snippet=snippet,
                                tags=tags
        )
        
        hot_threads.append(single_thread_summary)
    
    return ThreadSummaryResponse(threads=hot_threads, total=total)



async def getALLThreads():
    
      # get the thread_id and the updated_times arr for each thread_summary
    cursor = collection_conversations.find({}, {'thread_id': 1, 'updated_times': 1})

    thread_recent_replies_arr = []

    for doc in cursor:
        thread_id = doc['thread_id']
        updated_times = doc['updated_times']
        
        now = datetime.utcnow()
        four_days_ago = now - timedelta(days=4)

        # Filter datetime objects within the last 4 days
        filtered_date_times = [dt for dt in updated_times if dt >= four_days_ago]

        # Count the number of datetime objects within the last 4 days
        count_within_last_4_days = len(filtered_date_times)
        
        thread_recent_replies_arr.append({thread_id:count_within_last_4_days})
        
        
        
        

    sorted_thread_recent_replies_arr = sorted(thread_recent_replies_arr, key=lambda x: list(x.values())[0], reverse=True)
    
    
    hot_thread_ids = []
    
    if len(sorted_thread_recent_replies_arr) > 5:
        
        hot_thread_ids = [list(d.keys())[0] for d in sorted_thread_recent_replies_arr[:5]]
    
    else:
        hot_thread_ids = [list(d.keys())[0] for d in sorted_thread_recent_replies_arr]
    
    
    all_threads: List[GeneralThreadSummary] = []
    
    # add the info of hot_threads into the all_threads list
    for thread_id in hot_thread_ids:
        
        doc = collection_conversations.find_one({'thread_id': thread_id})
        
        subject = doc['subject']
        last_updated_time = doc['updated_times'][-1]
        summary = doc['summary']
        
        # Tokenize the summary into sentences
        sentences = nltk.tokenize.sent_tokenize(summary)

        # Get the first few sentences 
        num_sentences = 3
        snippet = ' '.join(sentences[:num_sentences])

        tags = doc['products']
        
        single_thread_summary = GeneralThreadSummary(
                                subject=subject, type='hot', lastUpdate=last_updated_time,
                                summary=summary,snippet=snippet,
                                tags=tags
        )
        
        all_threads.append(single_thread_summary)
        
    
    # get the non hot threads ids
    non_hot_thread_docs = collection_conversations.find({'thread_id': {'$nin': hot_thread_ids}}, {'thread_id': 1})
    non_hot_thread_ids = [doc['thread_id'] for doc in non_hot_thread_docs]
    
    # calculate total number of threads
    total = len(hot_thread_ids) + len(non_hot_thread_ids)
    
    
    # add the info of non_hot_threads into the all_threads list
    for thread_id in non_hot_thread_ids:
        
        doc = collection_conversations.find_one({'thread_id': thread_id})
        
        subject = doc['subject']
        last_updated_time = doc['updated_times'][-1]
        summary = doc['summary']
        
        # Tokenize the summary into sentences
        sentences = nltk.tokenize.sent_tokenize(summary)

        # Get the first few sentences 
        num_sentences = 3
        snippet = ' '.join(sentences[:num_sentences])

        tags = doc['products']
        
        single_thread_summary = GeneralThreadSummary(
                                subject=subject, 
                                type='normal', 
                                lastUpdate=last_updated_time,
                                summary=summary,
                                snippet=snippet,
                                tags=tags
        )
        
        all_threads.append(single_thread_summary)
    
    
    
    return AllThreadsSummaryResponse(threads=all_threads, total=total)
    