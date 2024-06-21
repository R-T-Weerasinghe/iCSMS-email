from datetime import date
from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException

from api.v2.dependencies.database import collection_issues, collection_inquiries, collection_suggestions

def getCompanyAddresses(type: str):
    """
    Get company addresses.
    """
    return_list = []
    if type == "issue":
        pass
    elif type == "inquiry":
        pass
    elif type == "suggestion":
        pass
    else:
        raise HTTPException(status_code=400, detail="Invalid type parameter provided.")
    return {"company_addresses": return_list}

def getClientAddresses(type: str):
    """
    Get client addresses.
    """
    return_list = []
    if type == "issue":
        pass
    elif type == "inquiry":
        pass
    elif type == "suggestion":
        pass
    else:
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
        return_list = ["new", "waiting", "update", "closed"]
    else:
        raise HTTPException(status_code=400, detail="Invalid type parameter provided.")
    return {"status": return_list}


def getTags(type: str):
    """
    Get tags.
    """
    return_list = []
    if type == "issue":
        pass
    elif type == "inquiry":
        pass
    elif type == "suggestion":
        pass
    else:
        raise HTTPException(status_code=400, detail="Invalid type parameter provided.")
    return {"tags": return_list}
