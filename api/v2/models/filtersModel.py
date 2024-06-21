from typing import List, Optional, Literal
from pydantic import BaseModel, Field, SerializeAsAny, field_validator
from datetime import date
from fastapi import Query
from .utilsModel import parse_to_list


class Tags(BaseModel):
    tags: List[str]


class Statuses(BaseModel):
    status: List[str]


class CompanyAddresses(BaseModel):
    company_addresses: List[str]


class ClientAddresses(BaseModel):
    client_addresses: List[str]


class FilterParams(BaseModel):
    # NOTE: SerializeAsAny is used to suppress a *warning* given by Pydantic when handling arrays. This is a bug in Pydantic.
    # NOTE: Moreinfo: https://github.com/pydantic/pydantic/issues/7905
    r: Optional[SerializeAsAny[str]] = Field(
        Query(None, description="Recipient email addresses"))
    s: Optional[SerializeAsAny[str]] = Field(
        Query(None, description="Sender email addresses"))
    tags: Optional[SerializeAsAny[str]] = Field(
        Query(None, description="Tags associated with the issue"))
    allTags: Optional[bool] = Field(
        Query(None, description="Indicates if all tags should be present"))
    status: Optional[SerializeAsAny[str]] = Field(
        Query(None, description="Status of the issue"))
    dateFrom: Optional[date] = Field(
        Query(None, description="Start date for the issue (inclusive)"))
    dateTo: Optional[date] = Field(
        Query(None, description="End date for the issue (inclusive)"))
    q: Optional[str] = Field(Query(None, description="Search query"))
    new: Optional[bool] = Field(
        Query(None, description="Indicates if the issue is new"))
    imp: Optional[bool] = Field(
        Query(None, description="Indicates if the issue is important"))
    skip: int = Field(
        Query(None, description="Number of records to skip"), ge=0)
    limit: int = Field(
        Query(None, description="Number of records to return"), ge=1, le=100)

    _to_list = field_validator('r', 's', 'tags', 'status')(parse_to_list)


class FilterTypeParams(BaseModel):
    type: Literal['issue', 'inquiry', 'suggestion'] = Field(
        Query(None, description="Type of filter data to be returned"))
