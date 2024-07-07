import os
from fastapi import APIRouter, HTTPException

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from api.email_authorization.services import init_oauth_flow, init_oauth_flow_sending
from google_auth_oauthlib.flow import Flow # type: ignore
from pathlib import Path

from api.email_filtering_and_info_generation.configurations.database import collection_configurations


router = APIRouter()

@router.get("/info_and_retrieval/callback")
async def callback(request: Request, id: int):
    
    
    # print("Received callback request:")
    # print(f"Query parameters: {request.query_params}")
    # print(f"Path parameters: {request.path_params}")
    # print(f"Headers: {request.headers}")
    # print(f"Body: {await request.body()}")
    # print("in the CALLBACK'")

    try:
        # Print the query parameters received in the request
        print("Query Parameters:", dict(request.query_params))

        
        # Extract query parameters
        state = request.query_params.get('state')
        code = request.query_params.get('code')

        
        # Handle the rest of the callback logic here
        client_secrets_file = f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{id}/client_secret.json"  
        redirect_uri = f'http://127.0.0.1:8000/email/info_and_retrieval/callback?id={id}'
        flow = init_oauth_flow(client_secrets_file, redirect_uri)
        flow.fetch_token(authorization_response=str(request.url))
        
        credentials = flow.credentials
        token_path = f'api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{id}/gmail_token.json'
        
        # Delete the existing file if it exists
        if os.path.exists(token_path):
            os.remove(token_path)
        
        print("credentials", credentials)
        credentials_dict_string = credentials.to_json()

        
        # Write the new credentials
        with open(token_path, 'w') as token_file:
            token_file.write(credentials_dict_string)
        
        doc = {"id":2, "needToAuthorize":False, "needToAuthorizeAddress":"" ,"authorization_url":""}
        collection_configurations.update_one({"id": 2}, {"$set": doc}) 
            
        # Optionally, you can redirect or return a response here
        return {"message": "Authentication successful"}
        
    except Exception as e:
        # Print any exceptions that occur during callback processing
        print("Error in callback:", e)
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.get("/info_and_retrieval/callbackSending")
async def callback(request: Request, id: int):
    
    
    # print("Received callback request:")
    # print(f"Query parameters: {request.query_params}")
    # print(f"Path parameters: {request.path_params}")
    # print(f"Headers: {request.headers}")
    # print(f"Body: {await request.body()}")
    # print("in the CALLBACK'")

    try:
        # Print the query parameters received in the request
        print("Query Parameters:", dict(request.query_params))

        
        # Extract query parameters
        state = request.query_params.get('state')
        code = request.query_params.get('code')

        
        # Handle the rest of the callback logic here
        client_secrets_file = f"api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{id}/client_secret.json"  
        redirect_uri = f'http://127.0.0.1:8000/email/info_and_retrieval/callbackSending?id={id}'
        flow = init_oauth_flow_sending(client_secrets_file, redirect_uri)
        flow.fetch_token(authorization_response=str(request.url))
        
        credentials = flow.credentials
        token_path = f'api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{id}/gmail_token.json'
        
        # Delete the existing file if it exists
        if os.path.exists(token_path):
            os.remove(token_path)
        
        print("credentials", credentials)
        credentials_dict_string = credentials.to_json()

        
        # Write the new credentials
        with open(token_path, 'w') as token_file:
            token_file.write(credentials_dict_string)
        
        doc = {"id":2, "needToAuthorize":False, "needToAuthorizeAddress":"" ,"authorization_url":""}
        collection_configurations.update_one({"id": 2}, {"$set": doc}) 
            
        # Optionally, you can redirect or return a response here
        return {"message": "Authentication successful"}
        
    except Exception as e:
        # Print any exceptions that occur during callback processing
        print("Error in callback:", e)
        raise HTTPException(status_code=500, detail="Internal server error")
    

# ----------------------------------------  email permissions authorization API calls -----------------------------------------


@router.get("/info_and_retrieval/get_need_for_authorization")
async def get_need_for_authorization():
    
    document = collection_configurations.find_one({"id": 2})

    if document:
        need_to_authorize = document.get("needToAuthorize")
        if need_to_authorize is not None:
            result =  {"needToAuthorize": need_to_authorize}
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=404, detail="Field 'needToAuthorize' not found in document")
    else:
        raise HTTPException(status_code=404, detail="Document with id 2 not found")
    

@router.get("/info_and_retrieval/get_authorization_info")
async def get_authorization_info():
    
    document = collection_configurations.find_one({"id": 2})

    if document:
        need_to_authorize = document.get("needToAuthorize")
        needToAuthorizeAddress = document.get("needToAuthorizeAddress")
        authorization_url = document.get("authorization_url")
        
        result = {"need_to_authorize":need_to_authorize, "needToAuthorizeAddress":needToAuthorizeAddress, "authorization_url":authorization_url}
        return JSONResponse(content=result)
    else:
        raise HTTPException(status_code=404, detail="Document with id 2 not found")