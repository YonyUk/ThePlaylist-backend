from fastapi import Depends
from repositories import get_user_repository,UserRepository
from .user import UserService
from .auth import AuthService

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