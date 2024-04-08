import os



def integrateEmail(dict_array):

    new_email_address=input("Enter email address ")
    new_email_client_secret_content=input("copy and paste here the content of the client_secret.json file ")
    new_email_nickname=input("enter a nickname for the new email address ")

    # get the id of the new email account
    if len(dict_array)!=0:
        # Find the maximum id value of the current dict_array
        max_id = max(int(d["id"]) for d in dict_array)

        # Increment the id value for the new dictionary
        new_id = str(max_id + 1)
    else:
        new_id=1

    new_dict = {"id": new_id, "address": new_email_address, "nickname": new_email_nickname}

    dict_array.append(new_dict)



    new_folder_path= f"credentialsForEmails/credentialsForEmail{new_id}"
    os.makedirs(new_folder_path, exist_ok=True)

    file_name = f"{new_folder_path}/client_secret.json"

    # Open the file in write mode (this will create the file if it doesn't exist)
    with open(file_name, "w") as file:
        # Optionally, you can write some initial content to the file
        file.write(new_email_client_secret_content)

    return dict_array



