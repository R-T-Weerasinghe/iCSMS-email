import boto3
import authentication


def analyze_sentiment(text):
    """
    Analyze sentiment of the given text
    :param text: text to analyze
    :return: sentiment of the text
    """
    comprehend = boto3.client(service_name='comprehend', aws_access_key_id=authentication.aws_access_key_id,
                              aws_secret_access_key=authentication.aws_secret_access_key,
                              region_name=authentication.region_name)
    response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    return response.get('Sentiment')
