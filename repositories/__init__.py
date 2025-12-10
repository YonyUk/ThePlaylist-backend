from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_database_session
from .user import UserRepository

def get_user_repository(db:AsyncSession=Depends(get_database_session)):
    '''
    Docstring for get_user_repository
    
    :param db: database session dependency
    :type db: AsyncSession
    :return: the 'UserRepository' dependency
    :rtype: UserRepository
    '''
    repository = UserRepository(db)
    try:
        yield repository
    finally:
        repository = None