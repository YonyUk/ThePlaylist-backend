from fastapi import Depends, HTTPException, Request,status
from repositories import get_user_repository,UserRepository
from .user import UserService
from .auth import AuthService,_oauth2_schema
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer

_http_security = HTTPBearer(auto_error=False)

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
    request:Request,
    credentials:HTTPAuthorizationCredentials=Depends(_http_security),
    service:AuthService=Depends(get_auth_service)
):
    token = None
    if credentials:
        token = credentials.credentials
    
    if not token:
        token = request.cookies.get('access_token')
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Missing authorization token from cookies',
            headers={'WWW-Authenticate':'Bearer'}
        )
    return await service.get_current_user(token)