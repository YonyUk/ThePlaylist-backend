from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,exists
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from .repository import Repository
from .user import UserRepository
from models import Track,Playlist
from models.track import (
    tracks_likes as likes,
    tracks_dislikes as dislikes,
    tracks_loves as loves,
    playlists_tracks
)
import logging

logger = logging.getLogger(__name__)

class TrackRepository(Repository):

    def __init__(self,db: AsyncSession,user_repository:UserRepository):
        super().__init__(Track, db)
        self._user_repository = user_repository
        self._likes = likes
        self._dislikes = dislikes
        self._loves = loves
        self._playlists_tracks = playlists_tracks
    
    async def _try_get_instance(self, instance: Track) -> Track | None:
        db_instance = await self.get_by_id(str(instance.id))
        if not db_instance:
            query = select(Track).where(Track.content_hash==instance.content_hash)
            result = await self._db.execute(query)
            return result.scalar_one_or_none()
    
    async def liked_by(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for liked_by
        
        :type user_id: str
        :type track_id: str
        :rtype: bool
        '''
        query = select(exists().where(
            (self._likes.columns.track_id==track_id)
            & (self._likes.columns.user_id==user_id)
        ))
        result = await self._db.execute(query)
        return result.scalar() == True

    async def disliked_by(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for disliked_by
        
        :type user_id: str
        :type track_id: str
        :rtype: bool
        '''
        query = select(exists().where(
            (self._dislikes.columns.track_id==track_id)
            & (self._dislikes.columns.user_id==user_id)
        ))
        result = await self._db.execute(query)
        return result.scalar() == True
    
    async def loved_by(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for loved_by
        
        :type user_id: str
        :type track_id: str
        :rtype: bool
        '''
        query = select(exists().where(
            (self._loves.columns.track_id==track_id)
            & (self._loves.columns.user_id==user_id)
        ))
        result = await self._db.execute(query)
        return result.scalar() == True

    async def add_like_from_user_to_track(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for add_like_from

        Adds a like from given user

        :type user_id: str
        :type track_id: str
        :rtype: bool
        '''
        query = select(Track).where(Track.id==track_id).options(selectinload(Track.users_likes))
        result = await self._db.execute(query)
        db_track = result.scalar_one_or_none()
        if not db_track:
            return False
        db_user = await self._user_repository.get_by_id(user_id)
        if not db_user:
            return False
        try:
            db_track.users_likes.append(db_user)
            await self._db.commit()
            await self._db.refresh(db_track)
            return True
        except IntegrityError as e:
            logger.error(f'Integrity error while adding like: {e}')
            await self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f'Database error while adding like: {e}')
            await self._db.rollback()
            return False
        except Exception as e:
            logger.error(f'An unexpected error has ocurred while adding like: {e}')
            await self._db.rollback()
            return False
    
    async def remove_like_from_user_to_track(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for remove_like_from_user_to_track
        
        Remove a like from the given user

        :type user_id: str
        :type track_id: str
        :rtype: bool
        '''
        query = select(Track).where(Track.id==track_id).options(selectinload(Track.users_likes))
        result = await self._db.execute(query)
        db_track = result.scalar_one_or_none()
        if not db_track:
            return False
        db_user = await self._user_repository.get_by_id(user_id)
        if not db_user:
            return False
        try:
            db_track.users_likes.remove(db_user)
            await self._db.commit()
            await self._db.refresh(db_track)
            return True
        except IntegrityError as e:
            logger.error(f'Integrity error while deleting like: {e}')
            await self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f'Database error while deleting like: {e}')
            await self._db.rollback()
            return False
        except Exception as e:
            logger.error(f'An unexpected error has ocurred while deleting like: {e}')
            await self._db.rollback()
            return False
    
    async def add_dislike_from_user_to_track(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for add_dislike_from_user_to_track

        Adds a dislike from the given user
                
        :type user_id: str
        :type track_id: str
        :rtype: bool
        '''

        query = select(Track).where(Track.id==track_id).options(selectinload(Track.users_dislikes))
        result = await self._db.execute(query)
        db_track = result.scalar_one_or_none()
        if not db_track:
            return False
        db_user = await self._user_repository.get_by_id(user_id)
        if not db_user:
            return False
        try:
            db_track.users_dislikes.append(db_user)
            await self._db.commit()
            await self._db.refresh(db_track)
            return True
        except IntegrityError as e:
            logger.error(f'IntegrityError while adding dislike: {e}')
            await self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f'Database error while adding dislike: {e}')
            await self._db.rollback()
            return False
        except Exception as e:
            logger.error(f'An unexpected error has ocurred while adding dislike: {e}')
            await self._db.rollback()
            return False
    
    async def remove_dislike_from_user_to_track(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for remove_dislike_from_user_to_track

        Remove a dislike from the given user
                
        :type user_id: str
        :type track_id: str
        :rtype: bool
        '''

        query = select(Track).where(Track.id==track_id).options(selectinload(Track.users_dislikes))
        result = await self._db.execute(query)
        db_track = result.scalar_one_or_none()
        if not db_track:
            return False
        db_user = await self._user_repository.get_by_id(user_id)
        if not db_user:
            return False
        try:
            db_track.users_dislikes.remove(db_user)
            await self._db.commit()
            await self._db.refresh(db_track)
            return True
        except IntegrityError as e:
            logger.error(f'IntegrityError while deleting dislike: {e}')
            await self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f'Database error while deleting dislike: {e}')
            await self._db.rollback()
            return False
        except Exception as e:
            logger.error(f'An unexpected error has ocurred while deleting dislike: {e}')
            await self._db.rollback()
            return False
        
    async def add_love_from_user_to_track(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for add_love_from_user_to_track

        Adds a love from the given user
                
        :type user_id: str
        :type track_id: str
        :rtype: bool
        '''
        query = select(Track).where(Track.id==track_id).options(selectinload(Track.users_loves))
        result = await self._db.execute(query)
        db_track = result.scalar_one_or_none()
        if not db_track:
            return False
        db_user = await self._user_repository.get_by_id(user_id)
        if not db_user:
            return False
        try:
            db_track.users_loves.append(db_user)
            await self._db.commit()
            await self._db.refresh(db_track)
            return True
        except IntegrityError as e:
            logger.error(f'IntegrityError while adding love: {e}')
            await self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f'Database error while adding love: {e}')
            await self._db.rollback()
            return False
        except Exception as e:
            logger.error(f'An unexpected error has ocurred while adding love: {e}')
            await self._db.rollback()
            return False
        
    async def remove_love_from_user_to_track(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for remove_love_from_user_to_track
        
        :type user_id: str
        :type track_id: str
        :rtype: bool
        '''
        query = select(Track).where(Track.id==track_id).options(selectinload(Track.users_loves))
        result = await self._db.execute(query)
        db_track = result.scalar_one_or_none()
        if not db_track:
            return False
        db_user = await self._user_repository.get_by_id(user_id)
        if not db_user:
            return False
        try:
            db_track.users_loves.remove(db_user)
            await self._db.commit()
            await self._db.refresh(db_track)
            return True
        except IntegrityError as e:
            logger.error(f'IntegrityError while deleting love: {e}')
            await self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f'Database error while deleting love: {e}')
            await self._db.rollback()
            return False
        except Exception as e:
            logger.error(f'An unexpected error has ocurred while deleting love: {e}')
            await self._db.rollback()
            return False

    async def get_tracks_uploaded_by(self,user_id:str,limit:int=100,skip:int=0) -> Sequence[Track]:
        '''
        Docstring for get_tracks_uploaded_by
        
        :type user_id: str
        :type limit: int
        :param skip: limit of results per query
        :type skip: number of register to jump
        :rtype: Sequence[Track]
        '''
        query = select(Track).where(Track.uploaded_by==user_id).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return result.scalars().all()

    async def get_tracks_with_name_like(self,text:str,limit:int=100,skip:int=0) -> Sequence[Track]:
        '''
        Docstring for get_tracks_with_name_like
        
        :type text: str
        :param limit: limit of results per query
        :type limit: int
        :param skip: number of registers to jump
        :type skip: int
        :rtype: Sequence[Track]
        '''
        query = select(Track).where(Track.name.like(f'%{text}%')).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return result.scalars().all()
    
    async def get_tracks_from_user_with_name_like(
        self,
        user_id:str,
        text:str,
        limit:int=100,
        skip:int=0
    ) -> Sequence[Track]:
        '''
        Docstring for get_tracks_from_user_with_name_like
        
        :type user_id: str
        :type text: str
        :param limit: limit of results per query
        :type limit: int
        :param skip: number of registers to jump
        :type skip: int
        :rtype: Sequence[Track]
        '''
        query = select(Track).where(
            (Track.name.like(f'%{text}%')) &
            (Track.uploaded_by==user_id)
        ).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return result.scalars().all()
    
    async def get_tracks_on_playlist(self,playlist_id:str) -> Sequence[Track]:
        '''
        Docstring for get_tracks_on_playlist
        
        :type playlist_id: str
        :rtype: Sequence[Track]
        '''
        query = select(Track).join(Track.playlists).where(Playlist.id==playlist_id)
        result = await self._db.execute(query)
        return result.scalars().all()