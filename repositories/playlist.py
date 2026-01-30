from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from sqlalchemy import select,exists,func
from sqlalchemy.orm import selectinload
from .repository import Repository
from .track import TrackRepository
from .user import UserRepository
from models import Playlist,Track,User
from models.track import playlists_tracks as tracks
from models.playlist import (
    playlists_likes as likes,
    playlists_dislikes as dislikes,
    playlists_loves as loves
)
import logging

logger = logging.getLogger(__name__)

class PlaylistRepository(Repository[Playlist]):

    def __init__(self,db: AsyncSession,track_repository:TrackRepository,user_repository:UserRepository):
        super().__init__(Playlist, db)
        self._track_repository = track_repository
        self._tracks = tracks
        self._user_repository = user_repository
        self._likes = likes
        self._dislikes = dislikes
        self._loves = loves
    
    async def _try_get_instance(self, instance: Playlist) -> Playlist | None:
        return await self.get_by_id(str(instance.id))
    
    async def liked_by(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for liked_by
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        query = select(exists().where(
            (self._likes.columns.playlist_id==playlist_id) &
            (self._likes.columns.user_id==user_id)
        ))
        result = await self._db.execute(query)
        return result.scalar() == True
    
    async def disliked_by(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for disliked_by
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        query = select(exists().where(
            (self._dislikes.columns.playlist_id==playlist_id) &
            (self._dislikes.columns.user_id==user_id)
        ))
        result = await self._db.execute(query)
        return result.scalar() == True
    
    async def loved_by(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for loved_by
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        query = select(exists().where(
            (self._loves.columns.playlist_id==playlist_id) &
            (self._loves.columns.user_id==user_id)
        ))
        result = await self._db.execute(query)
        return result.scalar() == True

    async def add_like_from_user_to_playlist(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for add_like_from_user_to_playlist
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        query = select(Playlist).where(Playlist.id==playlist_id).options(selectinload(Playlist.users_likes))
        result = await self._db.execute(query)
        db_playlist = result.scalar_one_or_none()
        if not db_playlist:
            return False
        db_user = await self._user_repository.get_by_id(user_id)
        if not db_user:
            return False
        try:
            db_playlist.users_likes.append(db_user)
            await self._db.commit()
            await self._db.refresh(db_playlist)
            return True
        except IntegrityError as e:
            logger.error(f'Integrity error while adding like: {e}')
            await self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f'Database error whiel adding like: {e}')
            await self._db.rollback()
            return False
        except Exception as e:
            logger.error(f'An unexpected error has ocurred while adding like: {e}')
            await self._db.rollback()
            return False
    
    async def remove_like_from_user_to_playlist(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for remove_like_from_user_to_playlist
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        query = select(Playlist).where(Playlist.id==playlist_id).options(selectinload(Playlist.users_likes))
        result = await self._db.execute(query)
        db_playlist = result.scalar_one_or_none()
        if not db_playlist:
            return False
        db_user = await self._user_repository.get_by_id(user_id)
        if not db_user:
            return False
        try:
            db_playlist.users_likes.remove(db_user)
            await self._db.commit()
            await self._db.refresh(db_playlist)
            return True
        except IntegrityError as e:
            logger.error(f'Integrity error while removing like: {e}')
            await self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f'Database error whiel removing like: {e}')
            await self._db.rollback()
            return False
        except Exception as e:
            logger.error(f'An unexpected error has ocurred while removing like: {e}')
            await self._db.rollback()
            return False
    
    async def add_dislike_from_user_to_playlist(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for add_dislike_from_user_to_playlist
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        query = select(Playlist).where(Playlist.id==playlist_id).options(selectinload(Playlist.users_dislikes))
        result = await self._db.execute(query)
        db_playlist = result.scalar_one_or_none()
        if not db_playlist:
            return False
        db_user = await self._user_repository.get_by_id(user_id)
        if not db_user:
            return False
        try:
            db_playlist.users_dislikes.append(db_user)
            await self._db.commit()
            await self._db.refresh(db_playlist)
            return True
        except IntegrityError as e:
            logger.error(f'Integrity error while adding dislike: {e}')
            await self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f'Database error whiel adding dislike: {e}')
            await self._db.rollback()
            return False
        except Exception as e:
            logger.error(f'An unexpected error has ocurred while adding dislike: {e}')
            await self._db.rollback()
            return False
    
    async def remove_dislike_from_user_to_playlist(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for remove_dislike_from_user_to_playlist
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        query = select(Playlist).where(Playlist.id==playlist_id).options(selectinload(Playlist.users_dislikes))
        result = await self._db.execute(query)
        db_playlist = result.scalar_one_or_none()
        if not db_playlist:
            return False
        db_user = await self._user_repository.get_by_id(user_id)
        if not db_user:
            return False
        try:
            db_playlist.users_dislikes.remove(db_user)
            await self._db.commit()
            await self._db.refresh(db_playlist)
            return True
        except IntegrityError as e:
            logger.error(f'Integrity error while removing dislike: {e}')
            await self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f'Database error whiel removing dislike: {e}')
            await self._db.rollback()
            return False
        except Exception as e:
            logger.error(f'An unexpected error has ocurred while removing dislike: {e}')
            await self._db.rollback()
            return False

    async def add_love_from_user_to_playlist(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for add_love_from_user_to_playlist
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        query = select(Playlist).where(Playlist.id==playlist_id).options(selectinload(Playlist.users_loves))
        result = await self._db.execute(query)
        db_playlist = result.scalar_one_or_none()
        if not db_playlist:
            return False
        db_user = await self._user_repository.get_by_id(user_id)
        if not db_user:
            return False
        try:
            db_playlist.users_loves.append(db_user)
            await self._db.commit()
            await self._db.refresh(db_playlist)
            return True
        except IntegrityError as e:
            logger.error(f'Integrity error while adding love: {e}')
            await self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f'Database error whiel adding love: {e}')
            await self._db.rollback()
            return False
        except Exception as e:
            logger.error(f'An unexpected error has ocurred while adding love: {e}')
            await self._db.rollback()
            return False
    
    async def remove_love_from_user_to_playlist(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for remove_love_from_user_to_playlist
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        query = select(Playlist).where(Playlist.id==playlist_id).options(selectinload(Playlist.users_loves))
        result = await self._db.execute(query)
        db_playlist = result.scalar_one_or_none()
        if not db_playlist:
            return False
        db_user = await self._user_repository.get_by_id(user_id)
        if not db_user:
            return False
        try:
            db_playlist.users_loves.remove(db_user)
            await self._db.commit()
            await self._db.refresh(db_playlist)
            return True
        except IntegrityError as e:
            logger.error(f'Integrity error while removing love: {e}')
            await self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f'Database error whiel removing love: {e}')
            await self._db.rollback()
            return False
        except Exception as e:
            logger.error(f'An unexpected error has ocurred while removing love: {e}')
            await self._db.rollback()
            return False

    async def add_track_to_playlist(self,playlist_id:str,track_id:str) -> bool:
        '''
        Docstring for add_track_to_playlist
        
        :type playlist_id: str
        :type track_id: str
        :rtype: bool
        '''
        db_playlist = await self.get_by_id(playlist_id)
        if not db_playlist:
            return False
        db_track = await self._track_repository.get_by_id(track_id)
        if not db_track:
            return False
        try:
            db_playlist.tracks.append(db_track)
            await self._db.commit()
            await self._db.refresh(db_playlist)
            return True
        except IntegrityError as e:
            logger.error(f'Integrity error while adding track {track_id} to playlist {playlist_id}')
            await self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f'Database error while adding track {track_id} to playlist {playlist_id}')
            await self._db.rollback()
            return False
        except Exception as e:
            logger.error(f'An unexpected error has ocurred: {e}')
            await self._db.rollback()
            return False
    
    async def remove_track_from_playlist(self,playlist_id:str,track_id:str) -> bool:
        '''
        Docstring for remove_track_from_playlist
        
        :type playlist_id: str
        :type track_id: str
        :rtype: bool
        '''
        db_playlist = await self.get_by_id(playlist_id)
        if not db_playlist:
            return False
        db_track = await self._track_repository.get_by_id(track_id)
        if not db_track:
            return False
        try:
            db_playlist.tracks.remove(db_track)
            await self._db.commit()
            await self._db.refresh(db_playlist)
            return True
        except IntegrityError as e:
            logger.error(f'Integrity error while deleting track {track_id} from playlist {playlist_id}')
            await self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f'Database error while deleting track {track_id} from playlist {playlist_id}')
            await self._db.rollback()
            return False
        except Exception as e:
            logger.error(f'An unexpected error has ocurred: {e}')
            await self._db.rollback()
            return False
        
    async def get_user_playlists(self,user_id:str,skip:int=0,limit:int=100) -> Sequence[Playlist]:
        '''
        Docstring for get_user_playlists
        
        :type user_id: str
        :param skip: number of register to skip
        :type skip: int
        :param limit: limit of results by query
        :type limit: int
        :rtype: Sequence[Playlist]
        '''
        query = select(Playlist).where(Playlist.author_id == user_id).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return result.scalars().all()
    
    async def exists_playlist_with_name_from_user(self,user_id:str,playlist_name:str) -> bool:
        '''
        Docstring for exists_playlist_with_name_from_user
        
        :type user_id: str
        :type playlist_name: str
        :rtype: bool
        '''
        query = select(exists().where((Playlist.author_id==user_id) & (Playlist.name==playlist_name)))
        result = await self._db.execute(query)
        return result.scalar() == True
    
    async def get_instances(self, limit: int = 100, skip: int = 0) -> Sequence[Playlist]:
        '''
        Docstring for get_instances
        
        :type limit: int
        :type skip: int
        :rtype: Sequence[Playlist]
        '''
        subquery = (
            select(1).where(
                (self._tracks.columns.playlist_id==Playlist.id) &
                (self._tracks.columns.track_id==Track.id)
            )
            .correlate(Playlist)
        )
        query = select(Playlist).where(exists(subquery)).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return result.scalars().all()
    
    async def search_playlists_by_name(self,text:str,limit:int=100,skip:int=0) -> Sequence[Playlist]:
        '''
        Docstring for search_playlist_by_name
        
        :type text: str
        :type limit: int
        :type skip: int
        :rtype: Sequence[Playlist]
        '''
        subquery = (
            select(1).where(
                (self._tracks.columns.playlist_id==Playlist.id) &
                (self._tracks.columns.track_id==Track.id)
            )
            .correlate(Playlist)
        )
        query = select(Playlist).where(exists(subquery)).where(Playlist.name.like(f'%{text}%')).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return result.scalars().all()
    
    async def search_playlists_by_author_name(self,text:str,limit:int=100,skip:int=0) -> Sequence[Playlist]:
        '''
        Docstring for search_playlist_by_author_name
        
        :type text: str
        :type limit: int
        :type skip: int
        :rtype: Sequence[Playlist]
        '''
        subquery = (
            select(1).where(
                (self._tracks.columns.playlist_id==Playlist.id) &
                (self._tracks.columns.track_id==Track.id)
            )
            .correlate(Playlist)
        )
        query = select(Playlist).where(exists(subquery)).join(Playlist.author).where(
            User.username.like(f'%{text}%')
        ).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return result.scalars().all()
    
    async def search_playlists_by_text(self,text:str,limit:int=100,skip:int=0) -> Sequence[Playlist]:
        '''
        Docstring for search_playlist_by_text
        
        :type text: str
        :type limit: int
        :type skip: int
        :rtype: Sequence[Playlist]
        '''
        subquery = (
            select(1).where(
                (self._tracks.columns.playlist_id==Playlist.id) &
                (self._tracks.columns.track_id==Track.id)
            )
            .correlate(Playlist)
        )
        query = select(Playlist).where(exists(subquery)).where(Playlist.name.like(f'%{text}%')).union(
            select(Playlist).where(exists(subquery)).join(Playlist.author).where(
                User.username.like(f'%{text}%')
            )
        ).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return result.scalars().all()