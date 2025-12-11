from fastapi import Depends
from repositories import get_user_repository,UserRepository
from .user import UserService
from .auth import AuthService,_oauth2_schema

def get_user_service(repository:UserRepository=Depends(get_user_repository)):
    service = UserService(repository)
    try:
        yield service
    finally:
        service = None

def get_auth_service(repository:UserRepository=Depends(get_user_repository)):
    service = AuthService(repository)
    try:
        yield service
    finally:
        service = None
    
async def get_current_user(
    token:str=Depends(_oauth2_schema),
    service:AuthService=Depends(get_auth_service)
):
    return await service.get_current_user(token)