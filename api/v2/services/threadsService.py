from fastapi import HTTPException
import nltk
from typing import List, Literal
from datetime import datetime, timedelta
from pydantic import ValidationError

from api.v2.models.threadsModel import ThreadSummary, GeneralThreadSummary, ThreadSummaryResponse, \
    AllThreadsSummaryResponse, ThreadInDB, ConvoSummaryResponse
from api.v2.dependencies.database import collection_conversations

nltk.download('punkt')

HOT_THREADS_INTERVAL = 30
HOT_THREADS_COUNT = 5
SNIPPET_LENGTH = 2


async def getHotThreads(
    hot_threads_interval: int = HOT_THREADS_INTERVAL,
    hot_threads_count: int = HOT_THREADS_COUNT,
    snippet_length: int = SNIPPET_LENGTH,
):

    now = datetime.now()
    last_x_days = now - timedelta(days=hot_threads_interval)
    hot_threads_pipeline = [
        # Match documents that have updated_times within the last x days
        {
            "$match": {
                "updated_times": {
                    "$elemMatch": {
                        "$gte": last_x_days,
                        "$lte": now
                    }
                }
            }
        },
        # Project the count of interactions within the last x days and the last updated time
        {
            "$addFields": {
                "interaction_count": {
                    "$size": {
                        "$filter": {
                            "input": "$updated_times",
                            "as": "time",
                            "cond": {
                                "$and": [
                                    {"$gte": ["$$time", last_x_days]},
                                    {"$lte": ["$$time", now]}
                                ]
                            }
                        }
                    }
                },
                "last_updated_time": {"$max": "$updated_times"}
            }
        },
        # Sort by interaction count and then by the last updated time
        {
            "$sort": {
                "interaction_count": -1,
                "last_updated_time": -1
            }
        },
        # Limit to the top y threads
        {
            "$limit": hot_threads_count
        }
    ]

    hot_threads = list(
        collection_conversations.aggregate(hot_threads_pipeline))
    try:
        hot_threads_objs = [ThreadInDB(**thread) for thread in hot_threads]
    except ValidationError:
        raise HTTPException(
            status_code=500, detail="Database schema error. Schema mismatch")

    returning_threads = []
    for thread_obj in hot_threads_objs:
        returning_threads.append(
            {
                "subject": thread_obj.subject,
                "snippet": ' '.join(nltk.tokenize.sent_tokenize(thread_obj.summary)[:snippet_length]).strip(),
                "summary": thread_obj.summary,
                # On the assumption that the last element is the most recent
                "lastUpdate": max(thread_obj.updated_times),
                "tags": thread_obj.products
            }
        )
    return ThreadSummaryResponse(
        threads=returning_threads,
        total=len(hot_threads)
    )

    # get the thread_id and the updated_times arr for each thread_summary
    cursor = collection_conversations.find(
        {}, {'thread_id': 1, 'updated_times': 1})
    thread_recent_replies_arr = []

    for doc in cursor:
        thread_id = doc['thread_id']
        updated_times = doc['updated_times']
        now = datetime.now()
        four_days_ago = now - timedelta(days=4)
        # Filter datetime objects within the last 4 days
        filtered_date_times = [
            dt for dt in updated_times if dt >= four_days_ago]
        # Count the number of datetime objects within the last 4 days
        count_within_last_4_days = len(filtered_date_times)
        thread_recent_replies_arr.append({thread_id: count_within_last_4_days})

    sorted_thread_recent_replies_arr = sorted(thread_recent_replies_arr, key=lambda x: list(x.values())[0],
                                              reverse=True)
    hot_thread_ids = [list(d.keys())[0]
                      for d in sorted_thread_recent_replies_arr[:5]]
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


async def getAllThreads(
    limit: int = 10,
    skip: int = 0,
    sort_by: Literal["update", "opened"] = "update",
    order: Literal["asc", "desc"] = "desc",
    hot_threads_interval: int = HOT_THREADS_INTERVAL,
    hot_threads_count: int = HOT_THREADS_COUNT,
    snippet_length: int = SNIPPET_LENGTH,
):
    """
    Retrieves all threads with their summaries and returns a response object containing the threads and total count.

    Args:
        limit (int, optional): The maximum number of threads to retrieve. Defaults to 10.
        skip (int, optional): The number of threads to skip. Defaults to 0.
        sort_by (Literal["update", "opened"], optional): The field to sort the threads by. Can be "update" or "opened". Defaults to "update".
        order (Literal["asc", "desc"], optional): The order in which to sort the threads. Can be "asc" or "desc". Defaults to "desc".
        hot_threads_interval (int, optional): The time interval (in days) to consider a thread as a hot thread. Defaults to 4.
        hot_threads_count (int, optional): The maximum number of hot threads to include in the response. Defaults to 4.
        snippet_length (int, optional): The number of sentences to include in the snippet. Defaults to 2.

    Returns:
        AllThreadsSummaryResponse: A response object containing the retrieved threads and the total count.
    """
    now = datetime.now()
    last_x_days = now - timedelta(days=hot_threads_interval)
    hot_threads_pipeline = [
        # Match documents that have updated_times within the last x days
        {
            "$match": {
                "updated_times": {
                    "$elemMatch": {
                        "$gte": last_x_days,
                        "$lte": now
                    }
                }
            }
        },
        # Project the count of interactions within the last x days and the last updated time
        {
            "$project": {
                "thread_id": 1,
                "interaction_count": {
                    "$size": {
                        "$filter": {
                            "input": "$updated_times",
                            "as": "time",
                            "cond": {
                                "$and": [
                                    {"$gte": ["$$time", last_x_days]},
                                    {"$lte": ["$$time", now]}
                                ]
                            }
                        }
                    }
                },
                "last_updated_time": {"$max": "$updated_times"}
            }
        },
        # Sort by interaction count and then by the last updated time
        {
            "$sort": {
                "interaction_count": -1,
                "last_updated_time": -1
            }
        },
        # Limit to the top y threads
        {
            "$limit": hot_threads_count
        },
        # Project only the thread_id
        {
            "$project": {
                "_id": 0,
                "thread_id": 1
            }
        }
    ]
    pipeline_all_threads = [
        {
            "$addFields": {
                "sort_index": {"$max": "$updated_times"} if sort_by == "update" else {"$min": "$updated_times"}
            }
        },
        {
            "$sort": {
                "sort_index": 1 if order == "asc" else -1
            }
        },
        {
            "$skip": skip
        },
        {
            "$limit": limit
        }
    ]
    # get the hot thread ids, sorted and limited, !! UNORDERED
    hot_thread_ids_dict = list(
        collection_conversations.aggregate(hot_threads_pipeline))
    # get the hot thread ids from the dict
    hot_thread_ids = [thread['thread_id'] for thread in hot_thread_ids_dict]
    # get all threads, sorted, limited and skipped
    all_threads = list(
        collection_conversations.aggregate(pipeline_all_threads))
    total_threads = collection_conversations.count_documents(
        {})  # get the total number of threads
    # END OF MONGO QUERIES

    try:
        all_threads_objs = [ThreadInDB(**thread) for thread in all_threads]
    except ValidationError:
        raise HTTPException(
            status_code=500, detail="Database schema error. Schema mismatch")

    returning_threads = []
    for thread_obj in all_threads_objs:
        returning_threads.append(
            {
                "subject": thread_obj.subject,
                "type": "hot" if thread_obj.thread_id in hot_thread_ids else "normal",
                "snippet": ' '.join(nltk.tokenize.sent_tokenize(thread_obj.summary)[:snippet_length]).strip(),
                "summary": thread_obj.summary,
                # On the assumption that the last element is the most recent
                "lastUpdate": max(thread_obj.updated_times),
                "tags": thread_obj.products
            }
        )
    return AllThreadsSummaryResponse(
        threads=returning_threads,
        total=total_threads,
        limit=limit,
        skip=skip
    )

    threads_sorted_by_update = sorted(
        threads, key=lambda x: x["updated_times"], reverse=True)
    now = datetime.now()
    for thread in threads:
        updated_count = thread["updated_times"]

    # get the thread_id and the updated_times arr for each thread_summary
    cursor = collection_conversations.find(
        {}, {'thread_id': 1, 'updated_times': 1})
    thread_recent_replies_arr = []

    for doc in cursor:
        thread_id = doc['thread_id']
        updated_times = doc['updated_times']
        now = datetime.now()
        four_days_ago = now - timedelta(days=4)
        # Filter datetime objects within the last 4 days
        filtered_date_times = [
            dt for dt in updated_times if dt >= four_days_ago]
        # Count the number of datetime objects within the last 4 days
        count_within_last_4_days = len(filtered_date_times)
        thread_recent_replies_arr.append({thread_id: count_within_last_4_days})

    sorted_thread_recent_replies_arr = sorted(thread_recent_replies_arr, key=lambda x: list(x.values())[0],
                                              reverse=True)

    hot_thread_ids = [list(d.keys())[0]
                      for d in sorted_thread_recent_replies_arr[:5]]
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
    non_hot_thread_docs = collection_conversations.find(
        {'thread_id': {'$nin': hot_thread_ids}}, {'thread_id': 1})
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
        raise HTTPException(status_code=404, detail=f"Thread with the thread id {
                            thread_id} not found")
    try:
        thread_obj = ThreadInDB(**thread)
    except ValidationError:
        raise HTTPException(
            status_code=500, detail="Database schema error. Schema mismatch")
    return ConvoSummaryResponse.convert(thread_obj)
