from fastapi import Depends
import jwt
import datetime as dt
from jwt import PyJWTError
from datetime import datetime,timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException,status
from schemas import AccessTokenSchema,AccessTokenDataSchema,UserSchema
from repositories import UserRepository
from settings import ENVIRONMENT

_oauth2_schema = OAuth2PasswordBearer(
    tokenUrl=f'{ENVIRONMENT.GLOBAL_API_PREFIX}/users/token'
)

class AuthService:

    def __init__(self,user_repository:UserRepository):
        self._user_repository = user_repository
        self._crypt_context = ENVIRONMENT.CRYPT_CONTEXT
    
    async def authenticate_user(self,username:str,password:str) -> bool:
        '''
        Docstring for authenticate_user
        
        :type username: str
        :type password: str
        :rtype: UserSchema | None
        '''

        user = await self._user_repository.get_by_name(username)
        if not user:
            return False
        if not self._crypt_context.verify(password,str(user.hashed_password)):
            return False
        return True
    
    def create_access_token(self,data:dict,expires_delta:timedelta | None = None) -> str:
        '''
        Docstring for create_access_token
        
        :param data: data for the token
        :type data: dict
        :param expires_delta: expire time for the token
        :type expires_delta: timedelta | None
        :return: a new access token
        :rtype: str
        '''
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(dt.timezone.utc) + expires_delta
        else:
            expire = datetime.now(dt.timezone.utc) + timedelta(minutes=ENVIRONMENT.TOKEN_LIFE_TIME)
        to_encode.update({'exp':expire})
        encoded_jwt = jwt.encode(
            to_encode,
            ENVIRONMENT.SECRET_KEY,
            algorithm=ENVIRONMENT.ALGORITHM
        )
        return encoded_jwt
    
    async def get_current_user(
        self,
        token:str
    ) -> UserSchema:
        '''
        Docstring for get_current_user
        
        :type token: str
        :rtype: UserSchema
        '''
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate':'Bearer'}
        )
        try:
            payload = jwt.decode(
                token,
                ENVIRONMENT.SECRET_KEY,
                algorithms=[ENVIRONMENT.ALGORITHM]
            )
            username:str = payload.get('sub')
            if not username:
                raise credentials_exception
            token_data = AccessTokenDataSchema(username=username)
        except PyJWTError:
            raise credentials_exception
        
        user = await self._user_repository.get_by_name(username)
        if not user:
            raise credentials_exception
        return user