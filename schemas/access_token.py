from pydantic import BaseModel

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