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
        super().__init__(User, repository, exclude_fields, exclude_unset)
        self._crypt_context = ENVIRONMENT.CRYPT_CONTEXT
    
    def _get_instance(self, **fields) -> User:
        password = fields['password']
        fields['hashed_password'] = self._crypt_context.hash(password)
        del fields['password']
        return super()._get_instance(**fields)
    
    async def get_by_name(self,username:str) -> UserSchema | None:
        '''
        Docstring for get_by_name
        
        :type username: str
        :rtype: UserSchema | None
        '''
        return await self._repository.get_by_name(username)
    
    async def get_by_email(self,email:str) -> UserSchema | None:
        '''
        Docstring for get_by_email
        
        :type email: str
        :rtype: UserSchema | None
        '''
        return await self._repository.get_by_email(email)