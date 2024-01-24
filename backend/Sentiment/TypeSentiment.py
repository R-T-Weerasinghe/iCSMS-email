from typing import TypedDict
from enum import Enum


class TextSpan(TypedDict):
    content: str
    beginOffset: int


class Sentence(TypedDict):
    text: str   # previously TextSpan
    score: float
    magnitude: float


# class Language(Enum):
#     """ For v2 of the API """
#     ENGLISH = "en"
#     FRENCH = "fr"
#     GERMAN = "de"
#     ITALIAN = "it"
#     JAPANESE = "ja"
#     KOREAN = "ko"
#     PORTUGUESE = "pt"
#     SPANISH = "es"
#     CHINESE_SIMPLIFIED = "zh"
#     CHINESE_TRADITIONAL = "zh-Hant"
#     DUTCH = "nl"
#     RUSSIAN = "ru"


class SentimentResponseObject(TypedDict):
    content: str
    score: float
    magnitude: float
    language: str
    sentences: list[Sentence]
    languageSupported: bool
