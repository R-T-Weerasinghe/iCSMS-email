from datetime import timedelta, datetime, date
from typing import List, Literal
from pymongo.collection import Collection
from api.v2.dependencies.database import collection_configurations
from api.v2.models.convoModel import EmailInDB


def get_overdue_datetime(opened_datetime: datetime) -> datetime:
    """
    Calculates the overdue date based on the opened_datetime and the overdue_margin_time
    from the configurations collection in the database.

    Parameters:
        opened_datetime (datetime): The date and time when the item was opened.

    Returns:
        datetime: The overdue date and time calculated by adding the overdue_margin_time to the opened_datetime.

    Raises:
        TypeError: If opened_datetime is not of type datetime.
    """

    config_doc = collection_configurations.find_one({"id": 1})
    overdue_margin: int = int(config_doc["overdue_margin_time"])
    overdue_date: datetime = opened_datetime + timedelta(days=overdue_margin)
    return overdue_date


def get_first_client_msg_time(email_list: List[EmailInDB], client_name="client") -> datetime | None:
    """
    Returns the time of the first client message in the email list

    Args:
        email_list: list of emails in the correct order
        client_name: name identifier used in database for the client

    Returns:
        time of the first client message or None
    """
    for email in email_list:
        if email.sender_type == client_name:
            return email.time
    return None


def get_first_response_time(email_list: List[EmailInDB], client_name="client", company_name="company") -> int | None:
    """
    Calculates the first response time of the company and outputs the time in minutes

    Args:
        email_list: list of emails in the correct order
        client_name: name identifier used in database for the client
        company_name: name identifier used in database for the company

    Returns:
        time in minutes or None
    """
    client_msg_time = None
    company_reply_time = None
    turn: Literal["client", "company", "done"] = "client"
    for email in email_list:
        if turn == "client" and email.sender_type == client_name:
            client_msg_time = email.time  # first client message
            turn = "company"
        elif turn == "company" and email.sender_type == company_name:
            company_reply_time = email.time  # first company msg after the first client msg
            turn = "done"

        if turn == "done":
            if company_reply_time < client_msg_time:
                raise ValueError("Invalid time in email list")
            first_response_time = (company_reply_time - client_msg_time).total_seconds() / 60  # in minutes
            return round(first_response_time)
    return None


def get_avg_response_time(email_list: List[EmailInDB], client_name="client", company_name="company") -> int | None:
    """
    Calculates the avg response time of the company and outputs the time in minutes

    Args:
        email_list: list of emails in the correct order
        client_name: name identifier used in database for the client
        company_name: name identifier used in database for the company

    Returns:
        time in minutes or None
    """
    client_msg_time = None
    company_reply_time = None
    response_times: List[float] = []
    turn: Literal["client", "company", "done"] = "client"
    for email in email_list:
        if turn == "client" and email.sender_type == client_name:
            client_msg_time = email.time
            turn = "company"
        elif turn == "company" and email.sender_type == company_name:
            company_reply_time = email.time
            turn = "done"

        if turn == "done":
            if company_reply_time < client_msg_time:
                raise ValueError("Invalid time in email list")
            response_time = (company_reply_time - client_msg_time).total_seconds() / 60
            response_times.append(response_time)
            turn = "client"
    if len(response_times) == 0:
        return None
    return round(sum(response_times) / len(response_times))


def get_resolution_time(
        email_list: List[EmailInDB], status: str, finished_status="closed",
        client_name="client", company_name="agent"
) -> int | None:
    """
    Calculates the total resolution time and outputs the time in minutes

    Args:
        email_list: list of emails in the correct order
        status: current status (of what we are considering)
        finished_status: string which will be provided as status when it(issue, inquiry) is closed
        client_name: name identifier used in database for the client
        company_name: name identifier used in database for the company

    Returns:
        time in minutes or None
    """
    if status != finished_status:
        return None
    first_email = email_list[0]
    last_email = email_list[-1]
    resolution_time = (last_email.time - first_email.time).total_seconds() / 60
    return round(resolution_time)


def build_query(
    skip: int,
    limit: int,
    type: Literal["issue", "inquiry", "suggestion"],
    company:List[str] = None,
    client: List[str] = None,
    tags: List[str] = None,
    allTags: bool = None,
    status: List[str] = None,
    dateFrom: date = None,
    dateTo: date = None,
    q: str = None,
) -> dict:
    """
    Build a query based on the given parameters.

    Args:
        skip: Number of records to skip.
        limit: Number of records to return.
        type: Type of query. (issue, inquiry, suggestion)
        company: List of company email addresses. (aka recipient)
        client: List of client email addresses. (aka sender)
        tags: List of tags associated with the issue.
        allTags: Indicates if all tags should be present.
        status: List of statuses of the issue.
        dateFrom: Start date for the issue (inclusive).
        dateTo: End date for the issue (inclusive).
        q: Search query.

    Returns:
        dict: The query dict document.
    """
    query = {}
    if type != "suggestion" and company:
        query["recepient_email"] = {"$in": company}
    if type == "suggestion" and company:
        query["recepient"] = {"$in": company}
    if client:
        query["sender_email"] = {"$in": client}
    if tags:
        if allTags:
            query["products"] = {"$all": tags}
        else:
            query["products"] = {"$in": tags}
    if status:
        query["$or"] = [{"status": {"$in": status}}, {"ongoing_status": {"$in": status}}]

    if type != "suggestion" and dateFrom and dateTo:
        query["start_time"] = {"$gte": datetime.combine(dateFrom, datetime.min.time()), "$lte": datetime.combine(dateTo, datetime.max.time())}
    if q:
        query["$text"] = {"$search": q}

    if type == "suggestion" and dateFrom and dateTo:
        query["date"] = {"$gte": datetime.combine(dateFrom, datetime.min.time()), "$lte": datetime.combine(dateTo, datetime.max.time())}
    return query


def search_between_collections(
        source: Collection,
        sink: Collection,
        limit: int,
        skip_: int,
        search_text: str,
        sink_query: str,
        source_field="subject",
        search_index="conversation_search_index",
) -> dict:
    """

    Args:
        source:
        sink:
        source_field:
        sink_query:

    Returns:

    """
    skip = skip_
    source_results = []
    # check aggregate returns a list (can return that is)
    source_results.append(list(source.aggregate(
        [
            {
                "$search": {
                    "index": search_index,
                    "text": {
                        "query": search_text,
                        "path": source_field
                    }
                }
            },
            {
                "$skip": skip
            },
            {
                "$limit": limit
            },
            {
                "$project": {
                    "thread_id": 1
                }
            },
        ]
    )))
    results_list = []
    results_list.append(sink.find())
