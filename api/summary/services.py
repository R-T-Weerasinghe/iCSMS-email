# business logic (i.e. normal codes, logic)

# example relative import
# from external_services.google_cloud import authentication
# end of example relative import

from database.db import get_conversations


def get_all_conversations():
    return get_conversations()
