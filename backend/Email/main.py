from new_emails import identify_new_emails

for email in identify_new_emails():
    print("senderEmail: ", email["senderEmail"])
    print("receiverEmail: ", email["receiverEmail"])
    print("sentTime: ", email["sentTime"])
    print("pulledTime: ", email["pulledTime"])
    print("emailId: ", email["emailId"])
    print("subject: ", email["subject"])
    print("\nbody:\n", email["body"])
    print("\n---------------------------------\n")