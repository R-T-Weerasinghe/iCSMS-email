from typing import List

from pydantic import BaseModel


class  SuggestionsData(BaseModel):
        receiver = str
        date = str
        products = List[str]
        suggestion = str