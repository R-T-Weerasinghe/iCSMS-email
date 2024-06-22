from fastapi import APIRouter, Depends
from api.v2.models.suggestionsModel import Suggestion, SuggestionsResponse
from api.v2.models.filtersModel import FilterParams
from api.v2.services.suggestionsService import getSuggestionByThreadId, getSuggestions


router = APIRouter()


@router.get("/suggestions", response_model=SuggestionsResponse, response_model_exclude_none=True, tags=["v2 - single email"])
def get_suggestions(params: FilterParams = Depends()):
    return getSuggestions(**params.model_dump())


@router.get("/suggestions/{id}", response_model=Suggestion, response_model_exclude_none=True, tags=["v2 - single email"])
def get_suggestion(id: str):
    return getSuggestionByThreadId(id)