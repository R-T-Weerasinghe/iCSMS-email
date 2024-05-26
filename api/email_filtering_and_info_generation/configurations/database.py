from pymongo import MongoClient

client = MongoClient("mongodb+srv://RaninduDBAdmin:kmHSROTUzj6keMhO@email.vm8njwj.mongodb.net/")


db = client["EmailDB"]

collection_email_msgs = db['EmailMessages']
collection_triger_events = db['TriggerEvents']
collection_trigers = db['Triggers']
collection_readingEmailAccounts=db['readingEmailAccounts']
collection_notificationSendingChannels = db['NotificationSendingChannels']
collection_suggestions = db['Suggestions']
collection_conversations = db['Conversations']
collection_issues = db['Issues']
collection_inquiries = db['Inquiries']
collection_overdue_trigger_events = db['OverdueTriggerEvents'] 
collection_configurations = db['Configurations'] 

 
  

