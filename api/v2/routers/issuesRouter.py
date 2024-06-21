from fastapi import APIRouter, Depends
from api.v2.models.issuesModel import Issue, IssuesResponse
from api.v2.models.filtersModel import FilterParams
from api.v2.services.issuesService import getIssueByThreadId, getIssues


router = APIRouter()


@router.get("/issues", response_model=IssuesResponse, response_model_exclude_none=True, tags=["v2 - single email"])
def get_issues(params: FilterParams = Depends()):
    return getIssues(**params.model_dump())


@router.get("/issues/{id}", response_model=Issue, response_model_exclude_none=True, tags=["v2 - single email"])
def get_issue(id: str):
    return getIssueByThreadId(id)