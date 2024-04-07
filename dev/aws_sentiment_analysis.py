from external_services.aws_comprehend.sentiment_analysis import analyze_sentiment
from pprint import pprint

def run():
    texts = [
        "It is bad",
        "It is the worst",
        "It was good, but now it is the worst",
        "My name is John Carpenter",
        "I am not satisfied with your service. The product I received was of poor quality and the customer support was unhelpful. I expected better from your company."
    ]

    for text in texts:
        pprint({
            "text": text,
            "score": analyze_sentiment(text)
        })

