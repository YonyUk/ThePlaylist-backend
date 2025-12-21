from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_database_session
from .user import UserRepository
from .playlist import PlaylistRepository
from .track import TrackRepository

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

def get_playlist_repository(db:AsyncSession=Depends(get_database_session)):
    '''
    Docstring for get_playlist_repository
    
    :param db: database session dependency
    :type db: AsyncSession
    :return: the 'PlaylistRepository' dependency
    :rtype: PlaylistRepository
    '''
    repository = PlaylistRepository(db)
    try:
        yield repository
    finally:
        repository = None

def get_track_repository(db:AsyncSession=Depends(get_database_session)):
    '''
    Docstring for get_track_repository
    
    :param db: database session dependency
    :type db: AsyncSession
    :return: the 'TrackRepository' dependency
    :rtype: TrackRepository
    '''
    repository = TrackRepository(db)
    try:
        yield repository
    finally:
        repository = None