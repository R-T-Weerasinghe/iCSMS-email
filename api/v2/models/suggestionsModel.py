from typing import List, Literal, Optional
from pydantic import BaseModel
from datetime import datetime

from .convoModel import EmailInDB, Email

class SuggestionInDB(BaseModel):
    suggestion: str
    products: List[str]
    date: datetime
    recepient: str


class Suggestion(BaseModel):
    suggestion: str
    tags: List[str]
    dateSuggested: datetime
    company: str

    @classmethod
    def convert(cls, suggestionInDB: SuggestionInDB) -> 'Suggestion':
        """
        Converts an SuggestionInDB object to an Suggestion object.
        """
        return cls(
            suggestion=suggestionInDB.suggestion,
            tags=suggestionInDB.products,
            dateSuggested=suggestionInDB.date,
            company=suggestionInDB.recepient
        )


class SuggestionsResponse(BaseModel):
    suggestions: List[Suggestion]
    total: int
    skip: int
    limit: int


