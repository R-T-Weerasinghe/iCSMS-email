from google.cloud import language_v2
from Sentiment.TypeSentiment import SentimentResponseObject, Sentence

# * to indicate that extra is a keyword-only argument


def analyze_sentiment(text_content: str, *, extra=False, accept_raw=False) -> SentimentResponseObject:
    """
    Analyzes Sentiment in a string.

    Args:
      text_content: The text content to analyze.
      extra: sentence-wise sentiment.
    """
    sentiment_response: SentimentResponseObject = {}

    client = language_v2.LanguageServiceClient()

    if accept_raw:
        document_type = language_v2.Document.Type.HTML
    else:
        document_type = language_v2.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    language_code = "en"
    document = {
        "content": text_content,
        "type_": document_type,
        "language_code": language_code,
    }

    # Available values: NONE, UTF8, UTF16, UTF32
    # See https://cloud.google.com/natural-language/docs/reference/rest/v2/EncodingType.
    encoding_type = language_v2.EncodingType.UTF8

    response = client.analyze_sentiment(
        request={"document": document, "encoding_type": encoding_type}
    )

    # Get overall sentiment of the input document
    sentiment_response["language"] = response.language_code
    sentiment_response["score"] = response.document_sentiment.score
    sentiment_response["magnitude"] = response.document_sentiment.magnitude
    sentiment_response["content"] = text_content
    
    if extra:
        # Get sentiment for all sentences in the document
        sentence_sentiment = Sentence()
        for sentence in response.sentences:
            sentence_sentiment["text"] = sentence.text.content
            sentence_sentiment["score"] = sentence.sentiment.score
            sentence_sentiment["magnitude"] = sentence.sentiment.magnitude

            sentiment_response.sentences.append(sentence_sentiment)

    return sentiment_response


