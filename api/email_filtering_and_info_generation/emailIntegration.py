import os
from api.email_filtering_and_info_generation.models import Reading_email_acc
from api.email_filtering_and_info_generation.services import send_reading_email_account, get_reading_emails_array



async def integrateEmail(new_email_address, new_email_nickname, new_email_client_secret_content):

    
    reading_email_acc_array = await get_reading_emails_array()
    
    
    # get the id of the new email account
    if reading_email_acc_array:
        # Find the maximum id value of the reading_email_acc_array
        max_id = max(int(d["id"]) for d in reading_email_acc_array) # type: ignore

        # Increment the id value for the new dictionary
        new_id = str(max_id + 1)
    else:
        new_id=1

    new_email_acc = Reading_email_acc(id=new_id, address=new_email_address, nickname=new_email_nickname)

    # send the new email account to the readingEmailAccounts collection
    respnse = await send_reading_email_account(new_email_acc.dict())
    
    print(respnse)



    new_folder_path= f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{new_id}"
    os.makedirs(new_folder_path, exist_ok=True)

    file_name = f"{new_folder_path}/client_secret.json"

    # Open the file in write mode (this will create the file if it doesn't exist)
    with open(file_name, "w") as file:
        # Optionally, you can write some initial content to the file
        file.write(new_email_client_secret_content)

 



