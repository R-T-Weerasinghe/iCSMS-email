# Authentication for google cloud

# example 
# external_services/google_cloud/authentication.py

import os
from google.oauth2 import service_account
from google.cloud import storage

def initialize_google_cloud_client():
    # Read authentication credentials from environment variables or a configuration file
    credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

    # Initialize Google Cloud client with authentication credentials
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    client = storage.Client(credentials=credentials)

    return client

# end of example