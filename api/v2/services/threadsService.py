from fastapi import HTTPException
import nltk
from typing import List
from datetime import datetime, timedelta

from pydantic import ValidationError

from api.v2.models.threadsModel import ThreadSummary, GeneralThreadSummary, ThreadSummaryResponse, \
    AllThreadsSummaryResponse, ThreadInDB, ConvoSummaryResponse
from api.v2.dependencies.database import collection_conversations

# TODO: Need to handle this differently. Download everytime when a request is made???
nltk.download('punkt')


async def getHotThreads():
    # TODO: Need refactoring !!!
    # get the thread_id and the updated_times arr for each thread_summary
    cursor = collection_conversations.find({}, {'thread_id': 1, 'updated_times': 1})
    thread_recent_replies_arr = []

    for doc in cursor:
        thread_id = doc['thread_id']
        updated_times = doc['updated_times']
        now = datetime.now()
        four_days_ago = now - timedelta(days=4)
        # Filter datetime objects within the last 4 days
        filtered_date_times = [dt for dt in updated_times if dt >= four_days_ago]
        # Count the number of datetime objects within the last 4 days
        count_within_last_4_days = len(filtered_date_times)
        thread_recent_replies_arr.append({thread_id: count_within_last_4_days})

    sorted_thread_recent_replies_arr = sorted(thread_recent_replies_arr, key=lambda x: list(x.values())[0],
                                              reverse=True)
    hot_thread_ids = [list(d.keys())[0] for d in sorted_thread_recent_replies_arr[:5]]
    total = len(hot_thread_ids)

    hot_threads: List[ThreadSummary] = []
    NUM_SENTENCES = 3
    for thread_id in hot_thread_ids:
        doc = collection_conversations.find_one({'thread_id': thread_id})
        subject = doc['subject']
        last_updated_time = doc['updated_times'][-1]
        summary = doc['summary']
        # Tokenize the summary into sentences
        sentences = nltk.tokenize.sent_tokenize(summary)
        # Get the first few sentences
        snippet = ' '.join(sentences[:NUM_SENTENCES])
        tags = doc['products']

        single_thread_summary = ThreadSummary(
            subject=subject, lastUpdate=last_updated_time,
            summary=summary, snippet=snippet,
            tags=tags
        )
        hot_threads.append(single_thread_summary)
    return ThreadSummaryResponse(threads=hot_threads, total=total)


async def getAllThreads():
    # get the thread_id and the updated_times arr for each thread_summary
    cursor = collection_conversations.find({}, {'thread_id': 1, 'updated_times': 1})
    thread_recent_replies_arr = []

    for doc in cursor:
        thread_id = doc['thread_id']
        updated_times = doc['updated_times']
        now = datetime.now()
        four_days_ago = now - timedelta(days=4)
        # Filter datetime objects within the last 4 days
        filtered_date_times = [dt for dt in updated_times if dt >= four_days_ago]
        # Count the number of datetime objects within the last 4 days
        count_within_last_4_days = len(filtered_date_times)
        thread_recent_replies_arr.append({thread_id: count_within_last_4_days})

    sorted_thread_recent_replies_arr = sorted(thread_recent_replies_arr, key=lambda x: list(x.values())[0],
                                              reverse=True)

    hot_thread_ids = [list(d.keys())[0] for d in sorted_thread_recent_replies_arr[:5]]
    all_threads: List[GeneralThreadSummary] = []

    # add the info of hot_threads into the all_threads list
    NUM_SENTENCES = 3
    for thread_id in hot_thread_ids:
        doc = collection_conversations.find_one({'thread_id': thread_id})
        subject = doc['subject']
        last_updated_time = doc['updated_times'][-1]
        summary = doc['summary']
        # Tokenize the summary into sentences
        sentences = nltk.tokenize.sent_tokenize(summary)
        # Get the first few sentences
        snippet = ' '.join(sentences[:NUM_SENTENCES])
        tags = doc['products']

        single_thread_summary = GeneralThreadSummary(
            subject=subject, type='hot', lastUpdate=last_updated_time,
            summary=summary, snippet=snippet,
            tags=tags
        )
        all_threads.append(single_thread_summary)

    # get the non-hot threads ids
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
        snippet = ' '.join(sentences[:NUM_SENTENCES])
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


def getThreadSummary(thread_id: str):
    thread: dict = collection_conversations.find_one({'thread_id': thread_id})
    if not thread:
        raise HTTPException(status_code=404, detail=f"Thread with the thread id {thread_id} not found")
    try:
        thread_obj = ThreadInDB(**thread)
    except ValidationError:
        raise HTTPException(status_code=500, detail="Database schema error. Schema mismatch")
    return ConvoSummaryResponse.convert(thread_obj)
