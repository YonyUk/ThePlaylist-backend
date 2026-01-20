from typing import Sequence
from repositories import PlaylistRepository
from models import Playlist
from schemas import PlaylistCreateSchema,PlaylistUpdateSchema,PlaylistSchema
from settings import ENVIRONMENT
from .service import Service

class PlaylistService(Service[
    Playlist,
    PlaylistRepository,
    PlaylistCreateSchema,
    PlaylistUpdateSchema,
    PlaylistSchema
]):
    
    def __init__(self,repository: PlaylistRepository,exclude_fields:set=set(), exclude_unset: bool = True):
        super().__init__(Playlist,PlaylistSchema,repository, exclude_fields, exclude_unset)
    
    async def add_track_to_playlist(self,playlist_id:str,track_id:str) -> bool:
        '''
        Docstring for add_track_to_playlist
        
        :type playlist_id: str
        :type track_id: str
        :rtype: bool
        '''
        return await self._repository.add_track_to_playlist(playlist_id,track_id)
    
    async def remove_track_from_playlist(self,playlist_id:str,track_id:str) -> bool:
        '''
        Docstring for remove_track_from_playlist
        
        :type playlist_id: str
        :type track_id: str
        :rtype: bool
        '''
        return await self._repository.remove_track_from_playlist(playlist_id,track_id)
    
    async def get_user_playlists(self,user_id:str,skip:int=0,limit:int=100) -> Sequence[PlaylistSchema]:
        '''
        Docstring for get_user_playlists
        
        :type user_id: str
        :param skip: number of registers to skip
        :type skip: int
        :param limit: limit of results by query
        :type limit: int
        :rtype: Sequence[PlaylistSchema]
        '''
        db_result = await self._repository.get_user_playlists(user_id,skip,limit)
        return [await self._to_schema(result) for result in db_result if result] # type: ignore
    
    async def exists_playlist_with_name_from_user(self,user_id:str,playlist_name:str) -> bool:
        '''
        Docstring for exists_playlist_with_name_from_user
        
        :type user_id: str
        :type playlist_name: str
        :rtype bool
        '''
        return await self._repository.exists_playlist_with_name_from_user(user_id,playlist_name)