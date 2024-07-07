from fastapi import HTTPException

from api.v2.dependencies.database import collection_issues, collection_inquiries, collection_suggestions


def getCompanyAddresses(type: str):
    """
    Get company addresses.
    """
    if type == "issue":
        return_list = collection_issues.distinct("recepient_email", {"recepient_email": {"$ne": None}})
    elif type == "inquiry":
        return_list = collection_inquiries.distinct("recepient_email", {"recepient_email": {"$ne": None}})
    elif type == "suggestion":
        return_list = collection_suggestions.distinct("recepient", {"recepient": {"$ne": None}})
    else:
        raise HTTPException(status_code=400, detail="Invalid type parameter provided.")
    return {"company_addresses": return_list}


def getClientAddresses(type: str):
    """
    Get client addresses.
    """
    if type == "issue":
        return_list = collection_issues.distinct("sender_email", {"sender_email": {"$ne": None}})
    elif type == "inquiry":
        return_list = collection_inquiries.distinct("sender_email", {"sender_email": {"$ne": None}})
    elif type == "suggestion":
        return_list = collection_suggestions.distinct("sender_email", {"sender_email": {"$ne": None}})
    else:
        # fail-safe: pydantic catches this before this function is called
        raise HTTPException(status_code=400, detail="Invalid type parameter provided.")
    return {"client_addresses": return_list}


def getStatuses(type: str):
    """
    Get statuses.
    """
    if type == "issue":
        return_list = ["new", "waiting", "update", "closed"]
    elif type == "inquiry":
        return_list = ["new", "waiting", "update", "closed"]
    elif type == "suggestion":
        return_list = ["new"]
    else:
        # fail-safe: pydantic catches this before this function is called
        raise HTTPException(status_code=400, detail="Invalid type parameter provided.")
    return {"status": return_list}


def getTags(type: str):
    """
    Get tags.
    """
    if type == "issue":
        return_list = collection_issues.distinct("products", {"products": {"$ne": None}})
    elif type == "inquiry":
        return_list = collection_inquiries.distinct("products", {"products": {"$ne": None}})
    elif type == "suggestion":
        return_list = collection_suggestions.distinct("products", {"products": {"$ne": None}})
    else:
        # fail-safe: pydantic catches this before this function is called
        raise HTTPException(status_code=400, detail="Invalid type parameter provided.")
    return {"tags": return_list}


