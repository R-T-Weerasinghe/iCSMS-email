from fastapi import APIRouter, Depends
from api.v2.models.inquiriesModel import InquiryDetailed, InquiriesResponse
from api.v2.models.filtersModel import FilterParams
from api.v2.services.inquiriesService import getInquiryByThreadId, getInquiries


router = APIRouter()


@router.get("/inquiries", response_model=InquiriesResponse, response_model_exclude_none=True, tags=["v2 - single email"])
def get_issues(params: FilterParams = Depends()):
    return getInquiries(**params.model_dump())


@router.get("/inquiries/{id}", response_model=InquiryDetailed, response_model_exclude_none=True, tags=["v2 - single email"])
def get_issue(id: str):
    return getInquiryByThreadId(id)