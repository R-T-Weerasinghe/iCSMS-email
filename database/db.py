from .mongodb import mongo
from .pipelines import pl_conversations
from utils.helpers import date_to_datetime

def get_conversations():
    """
    Retrieves a list of conversations from the database.

    Returns:
        list: A list of conversations.
    """
    collection = mongo.get_collection("Conversations")
    return list(collection.aggregate(pl_conversations))


def find_conversations(**kwargs):
    """
    Find conversations in the database based on the provided filters.

    Args:
        **kwargs: Keyword arguments representing the filters to apply.
            - subject (str): Filter conversations by subject.
            - sender (str): Filter conversations by sender.
            - receiver (str): Filter conversations by receiver.
            - start_date (datetime): Filter conversations by start date.
            - end_date (datetime): Filter conversations by end date.
            - sentiment_lower (float): Filter conversations by lower sentiment value.
            - sentiment_upper (float): Filter conversations by upper sentiment value.
            - limit (int): The number of conversations to return.
            - skip (int): The number of conversations to skip.
    Returns:
        list: A list of conversations matching the provided filters.

    Raises:
        ValueError: If either limit or skip is not provided.
    """

    collection = mongo.get_collection("Conversations")
    query = {}

    if "subject" in kwargs:
        query["subject"] = {"$regex": kwargs["subject"], "$options": "i"}

    if "sender" in kwargs:
        query["sender"] = {"$regex": kwargs["sender"], "$options": "i"}

    if "receiver" in kwargs:
        query["receiver"] = {"$regex": kwargs["receiver"], "$options": "i"}

    if "start_date" in kwargs and "end_date" in kwargs:
        query["date"] = {"$gte": kwargs["start_date"],
                         "$lte": kwargs["end_date"]}

    if "sentiment_lower" in kwargs and "sentiment_upper" in kwargs:
        query["summary.sentiment"] = {
            "$gte": kwargs["sentiment_lower"], "$lte": kwargs["sentiment_upper"]}

    limit = kwargs["limit"]
    skip = kwargs["skip"]

    if limit is None or skip is None:
        raise ValueError("Both limit and skip must be provided.")

    query = {key: date_to_datetime(value) for key, value in query.items()}

    return list(collection
                .find(query)
                .skip(skip)
                .limit(limit))


def find_emails(**kwargs):
    """
    Find emails in the database based on the provided search criteria.

    Args:
        **kwargs: Keyword arguments representing the search criteria.
            - subject (str): The subject of the email.
            - sender (str): The sender of the email.
            - receiver (str): The receiver of the email.
            - start_date (datetime): The start date for filtering emails.
            - end_date (datetime): The end date for filtering emails.
            - sentiment_lower (float): The lower bound of the sentiment score.
            - sentiment_upper (float): The upper bound of the sentiment score.
            - topic (list): A list of topics to filter emails.
            - limit (int): The number of emails to return.
            - skip (int): The number of emails to skip.
    Returns:
        list: A list of emails matching the search criteria.

    Raises:
        ValueError: If either limit or skip is not provided.
    """

    collection = mongo.get_collection("Emails")
    query = {}

    if "subject" in kwargs:
        query["subject"] = {"$regex": kwargs["subject"], "$options": "i"}

    if "sender" in kwargs:
        query["sender"] = {"$regex": kwargs["sender"], "$options": "i"}

    if "receiver" in kwargs:
        query["receiver"] = {"$regex": kwargs["receiver"], "$options": "i"}

    if "start_date" in kwargs and "end_date" in kwargs:
        query["datetime"] = {"$gte": kwargs["start_date"],
                             "$lte": kwargs["end_date"]}

    if "sentiment_lower" in kwargs and "sentiment_upper" in kwargs:
        query["our_sentiment_score"] = {
            "$gte": kwargs["sentiment_lower"], "$lte": kwargs["sentiment_upper"]}

    if "topic" in kwargs:
        query["topics"] = {"$in": kwargs["topic"]}

    limit = kwargs["limit"]
    skip = kwargs["skip"]

    if limit is None or skip is None:
        raise ValueError("Both limit and skip must be provided.")
    
    query = {key: date_to_datetime(value) for key, value in query.items()}
    
    return list(collection
                .find(query)
                .skip(skip)
                .limit(limit))
