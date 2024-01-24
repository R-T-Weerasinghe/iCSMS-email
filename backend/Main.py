from Email.new_emails import identify_new_emails
from Sentiment.analyzeSentiment import analyze_sentiment
from Sentiment.TypeSentiment import SentimentResponseObject
from Email.TypeEmail import Email
from Email.parse_html import html_to_text

email: Email

for email in identify_new_emails(return_raw=True):
    sentiment: SentimentResponseObject = analyze_sentiment(email["body"], accept_raw=True)
    print("---------------------------------------------------------------")
    print(html_to_text(sentiment["content"]))
    print("magnitude: ", sentiment["magnitude"])
    print("sentiment: ", sentiment["score"])
    print("---------------------------------------------------------------")
