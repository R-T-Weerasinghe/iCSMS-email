from fastapi import APIRouter, Depends
from api.v2.models.filtersModel import Tags, Statuses, CompanyAddresses, ClientAddresses, FilterTypeParams
from api.v2.services.filtersService import getCompanyAddresses, getClientAddresses, getStatuses, getTags

router = APIRouter()


@router.get("/filter/company-addresses", tags=["v2 - single email"], response_model=CompanyAddresses)
def get_company_addresses(params: FilterTypeParams = Depends()):
    return getCompanyAddresses(**params.model_dump())


@router.get("/filter/client-addresses", tags=["v2 - single email"], response_model=ClientAddresses)
def get_client_addresses(params: FilterTypeParams = Depends()):
    return getClientAddresses(**params.model_dump())


@router.get("/filter/statuses", tags=["v2 - single email"], response_model=Statuses)
def get_statuses(params: FilterTypeParams = Depends()):
    return getStatuses(**params.model_dump())


@router.get("/filter/tags", tags=["v2 - single email"], response_model=Tags)
def get_tags(params: FilterTypeParams = Depends()):
    return getTags(**params.model_dump())

