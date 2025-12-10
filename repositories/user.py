from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence
from models import User
from .repository import Repository

class UserRepository(Repository[User]):

    def __init__(self,db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self,email:str) -> User | None:
        '''
        Docstring for get_by_email
        
        :param email: email of the user
        :type email: str
        :return: the user who owns the given email
        :rtype: User | None
        '''
        query = select(User).where(User.email==email)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_name(self,username:str) -> User | None:
        '''
        Docstring for get_by_name
        
        :type username: str
        :return: the users with the same username
        :rtype: Sequence[User]
        '''
        query = select(User).where(User.username==username)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def _try_get_instance(self, instance: User) -> User | None:
        db_instance = await self.get_by_id(str(instance.id))
        if not db_instance:
            return await self.get_by_email(str(instance.email))
        return db_instance