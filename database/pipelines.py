
# This pipeline converts ObjectID to string for serialization at database level (better performance)
pl_conversations = [
    {
        '$project': {
            'id': {
                '$toString': '$_id'
            }, 
            '_id': 0, 
            'thread_id': 1, 
            'subject': 1, 
            'sentiment': 1, 
            'sender': 1, 
            'receiver': 1, 
            'summary': 1
        }
    }
]

