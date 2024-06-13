import requests
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

class Config:
    cognito_region = 'ap-south-1'
    cognito_pool_id = 'ap-south-1_YEH0sqfmB'
    cognito_app_client_id = '4nql0ttol3en0nir4d56ctdc6i'
    s3_bucket_name = 'cognito-user-profile-image'


class TokenPayload(BaseModel):
    sub: str
    roles: list
    username: str


cognito_region = Config.cognito_region
cognito_pool_id = Config.cognito_pool_id
cognito_app_client_id = Config.cognito_app_client_id
cognito_keys_url = f'https://cognito-idp.{cognito_region}.amazonaws.com/{cognito_pool_id}/.well-known/jwks.json'


def get_cognito_public_keys():
    response = requests.get(cognito_keys_url)
    response.raise_for_status()
    return response.json()['keys']


cognito_public_keys = get_cognito_public_keys()
security = HTTPBearer()


def decode_jwt(token: str):
    global cognito_public_keys
    try:
        header = jwt.get_unverified_header(token)
        key = next(k for k in cognito_public_keys if k['kid'] == header['kid'])
        return jwt.decode(token, key, algorithms=['RS256'], audience=cognito_app_client_id)
    except JWTError:
        # If verification fails, try to fetch the keys again
        header = jwt.get_unverified_header(token)
        cognito_public_keys = get_cognito_public_keys()
        try:
            key = next(k for k in cognito_public_keys if k['kid'] == header['kid'])
            return jwt.decode(token, key, algorithms=['RS256'], audience=cognito_app_client_id)
        except JWTError:
            raise HTTPException(status_code=403, detail="Could not validate credentials")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = decode_jwt(token)
    # print(payload)
    return TokenPayload(
        sub=payload['sub'],
        roles=payload.get('cognito:groups', []),
        username=payload['cognito:username']
    )


def role_required(required_role: str):
    def role_checker(user: TokenPayload = Depends(get_current_user)):
        # print(user)
        if required_role not in user.roles:
            raise HTTPException(status_code=403, detail="You do not have access to this resource")
        return user

    return role_checker
