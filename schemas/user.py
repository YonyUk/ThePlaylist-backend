from pydantic import BaseModel,EmailStr
from typing import Annotated
from pydantic.types import StringConstraints
from settings import ENVIRONMENT

class UserBaseSchema(BaseModel):
    '''
    Docstring for UserBaseSchema

    base schema for 'User' entity
    '''
    username:Annotated[
        str,
        StringConstraints(
            min_length=ENVIRONMENT.MIN_USERNAME_LENGTH,
            max_length=ENVIRONMENT.MAX_USERNAME_LENGTH
        )
    ]
    email:EmailStr

class UserCreateSchema(UserBaseSchema):
    '''
    Docstring for UserCreateSchema

    schema for 'User' entity creation
    '''
    password:Annotated[
        str,
        StringConstraints(
            min_length=ENVIRONMENT.MIN_USER_PASSWORD_LENGTH,
            max_length=ENVIRONMENT.MAX_USER_PASSWORD_LENGTH
        )
    ]

class UserUpdateSchema(UserCreateSchema):
    '''
    Docstring for UserUpdateSchema

    schema for 'User' entity updates
    '''

class UserSchema(UserBaseSchema):
    '''
    Docstring for UserSchema

    schema for 'User' entity responses
    '''
    id:str

    class Config:
        from_attributes = True