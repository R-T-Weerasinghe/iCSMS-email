from fastapi import APIRouter, Query, Depends
from api.v2.models.issuesModel import IssuesParams, IssuesResponse
from api.v2.services.issuesService import getIssues

router = APIRouter()

@router.get("/issues", response_model=IssuesResponse, tags=["v2 - single email"])
def get_issues(params: IssuesParams = Depends()):
    print("/emails/v2/issues endpoint called")
    return getIssues(**params.model_dump())