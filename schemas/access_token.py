from pydantic import BaseModel
from .user import UserSchema

class AccessTokenSchema(BaseModel):
    '''
    Docstring for AccessTokenSchema

    schema for an access token
    '''
    message:str
    token_type:str

class AccessTokenDataSchema(BaseModel):
    '''
    Docstring for AccessTokenDataSchema
    
    schema for the data of an access token
    '''
    username:str

class VerificationSchema(BaseModel):
    '''
    Docstring for VerificationSchema

    schema for Verification endpoint
    '''
    authenticated:bool
    user:UserSchema