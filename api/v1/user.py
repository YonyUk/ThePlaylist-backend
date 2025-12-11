from typing import Sequence
from datetime import timedelta
from fastapi import APIRouter,HTTPException,status,Depends,Query
from fastapi.security import OAuth2PasswordRequestForm
from schemas import UserSchema,UserCreateSchema,UserUpdateSchema,AccessTokenSchema
from services import AuthService,UserService,get_auth_service,get_user_service,get_current_user
from settings import ENVIRONMENT

router = APIRouter(prefix='/users',tags=['users'])

@router.post(
    '/register',
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED
)
async def register(
    user:UserCreateSchema,
    service:UserService=Depends(get_user_service)
):
    db_user = await service.get_by_name(user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'username "{user.username}" already exists'
        )
    db_user = await service.get_by_email(user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'email "{user.email}" already registered'
        )
    db_user = await service.create(user)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='an unexpected error has ocurred while registiring'
        )
    return db_user

@router.post(
    '/token',
    status_code=status.HTTP_201_CREATED,
    response_model=AccessTokenSchema
)
async def login_for_access_token(
    form_data:OAuth2PasswordRequestForm=Depends(),
    auth_service:AuthService=Depends(get_auth_service),
    user_service:UserService=Depends(get_user_service)
):
    authenticated = await auth_service.authenticate_user(form_data.username,form_data.password)
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authorization':'Bearer'}
        )
    user:UserSchema = await user_service.get_by_name(form_data.username) # type: ignore
    access_token_expires = timedelta(minutes=float(ENVIRONMENT.TOKEN_LIFE_TIME))
    access_token = auth_service.create_access_token(
        data={'sub':user.username},
        expires_delta=access_token_expires
    )
    return {'access_token':access_token,'token_type':'bearer'}

@router.get(
    '',
    response_model=Sequence[UserSchema],
    status_code=status.HTTP_200_OK
)
async def get_users(
    page:int=Query(0,description='page of results',ge=0),
    limit:int=Query(1,description='limit of results',ge=1),
    service:UserService=Depends(get_user_service)
):
    return await service.get(
        limit,
        page*ENVIRONMENT.PAGE_SIZE
    )

@router.get(
    '/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserSchema
)
async def get_user_by_id(
    user_id:str,
    service:UserService=Depends(get_user_service)
):
    db_user = await service.get_by_id(user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No user with id {user_id} was found'
        )
    return db_user

@router.put(
    '/{user_id}',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=UserSchema
)
async def update(
    user_id:str,
    user_data:UserUpdateSchema,
    service:UserService=Depends(get_user_service),
    current_user:UserSchema=Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Only can modify your own data'
        )
    db_user = await service.get_by_id(user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No user with id {user_id} was found'
        )
    db_user = await service.update(user_id,user_data)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has ocurred while updating'
        )
    return db_user

@router.delete(
    '/{user_id}',
    status_code=status.HTTP_202_ACCEPTED
)
async def delete(
    user_id:str,
    service:UserService=Depends(get_user_service),
    current_user:UserSchema=Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Only can modify your own data'
        )
    deleted = await service.delete(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has ocurred while deleting'
        )
    return {'message':'data deleted successfully'}