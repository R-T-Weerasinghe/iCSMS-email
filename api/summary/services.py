# business logic (i.e. normal codes, logic)

# example relative import
# from external_services.google_cloud import authentication
# end of example relative import

from database.db import get_conversations, find_conversations

def search_conversations(**query):
    query = {key: value for key, value in query.items() if value is not None}   # remove keys that have None values
    return find_conversations(**query)

def get_all_conversations():
    return get_conversations()
