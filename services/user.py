from fastapi import HTTPException,status
from repositories import UserRepository
from models import User
from schemas import UserCreateSchema,UserUpdateSchema,UserSchema
from settings import ENVIRONMENT
from .service import Service

class UserService(Service[
    User,
    UserRepository,
    UserCreateSchema,
    UserUpdateSchema,
    UserSchema
]):
    
    def __init__(
        self,
        repository: UserRepository,
        exclude_fields: set = set(),
        exclude_unset: bool = True
    ):
        super().__init__(User, UserSchema,repository, exclude_fields, exclude_unset)
        self._crypt_context = ENVIRONMENT.CRYPT_CONTEXT
    
    async def _get_instance(self, **fields) -> User:
        # breakpoint()
        if fields['password']:
            password = fields['password']
            fields['hashed_password'] = self._crypt_context.hash(password)
        else:
            db_instance = await self._repository.get_by_id(fields['id'])
            if not db_instance:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Could not found a user with id {fields['id']}'
                )
            fields['hashed_password'] = db_instance.hashed_password
        del fields['password']
        return await super()._get_instance(**fields)
    
    async def get_by_name(self,username:str) -> UserSchema | None:
        '''
        Docstring for get_by_name
        
        :type username: str
        :rtype: UserSchema | None
        '''
        db_user = await self._repository.get_by_name(username)
        return await self._to_schema(db_user)
    
    async def get_by_email(self,email:str) -> UserSchema | None:
        '''
        Docstring for get_by_email
        
        :type email: str
        :rtype: UserSchema | None
        '''
        db_user = await self._repository.get_by_email(email)
        return await self._to_schema(db_user)