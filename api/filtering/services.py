from database.db import find_emails

def search_emails(**query):
    query = {key: value for key, value in query.items() if value is not None}   # remove keys that have None values
    return find_emails(**query)