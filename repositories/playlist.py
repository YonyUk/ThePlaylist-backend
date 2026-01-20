from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from sqlalchemy import select,exists,func
from .repository import Repository
from .track import TrackRepository
from models import Playlist,Track
from models.track import playlists_tracks as tracks
import logging

logger = logging.getLogger(__name__)

class PlaylistRepository(Repository[Playlist]):

    def __init__(self,db: AsyncSession,track_repository:TrackRepository):
        super().__init__(Playlist, db)
        self._track_repository = track_repository
        self._tracks = tracks
    
    async def _try_get_instance(self, instance: Playlist) -> Playlist | None:
        return await self.get_by_id(str(instance.id))
    
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
        query = select(Playlist).where(exists(subquery))
        result = await self._db.execute(query)
        return result.scalars().all()