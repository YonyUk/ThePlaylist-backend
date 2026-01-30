from typing import Sequence
from repositories import PlaylistRepository
from models import Playlist
from schemas import PlaylistCreateSchema,PlaylistUpdateSchema,PlaylistSchema,ExistencialQuerySchema
from settings import ENVIRONMENT
from .service import Service
from enum import StrEnum

class PlaylistSearchMode(StrEnum):
    BY_NAME = 'by name'
    BY_AUTHOR = 'by author'
    BOTH = 'both'

class PlaylistService(Service[
    Playlist,
    PlaylistRepository,
    PlaylistCreateSchema,
    PlaylistUpdateSchema,
    PlaylistSchema
]):
    
    def __init__(self,repository: PlaylistRepository,exclude_fields:set=set(), exclude_unset: bool = True):
        super().__init__(Playlist,PlaylistSchema,repository, exclude_fields, exclude_unset)
    
    async def liked_by(self,user_id:str,playlist_id:str) -> ExistencialQuerySchema:
        '''
        Docstring for liked_by
        
        :type user_id: str
        :type playlist_id: str
        :rtype: ExistencialQuerySchema
        '''
        result = await self._repository.liked_by(user_id,playlist_id)
        return ExistencialQuerySchema(result=result)
    
    async def disliked_by(self,user_id:str,playlist_id:str) -> ExistencialQuerySchema:
        '''
        Docstring for disliked_by
        
        :type user_id: str
        :type playlist_id: str
        :rtype: ExistencialQuerySchema
        '''
        result = await self._repository.disliked_by(user_id,playlist_id)
        return ExistencialQuerySchema(result=result)
    
    async def loved_by(self,user_id:str,playlist_id:str) -> ExistencialQuerySchema:
        '''
        Docstring for loved_by
        
        :type user_id: str
        :type playlist_id: str
        :rtype: ExistencialQuerySchema
        '''
        result = await self._repository.loved_by(user_id,playlist_id)
        return ExistencialQuerySchema(result=result)
    
    async def add_like_from_user_to_playlist(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for add_like_from_user_to_playlist
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        return await self._repository.add_like_from_user_to_playlist(user_id,playlist_id)
    
    async def remove_like_from_user_to_playlist(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for remove_like_from_user_to_playlist
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        return await self._repository.remove_like_from_user_to_playlist(user_id,playlist_id)
    
    async def add_dislike_from_user_to_playlist(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for add_dislike_from_user_to_playlist
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        return await self._repository.add_dislike_from_user_to_playlist(user_id,playlist_id)
    
    async def remove_dislike_from_user_to_playlist(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for remove_dislike_from_user_to_playlist
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        return await self._repository.remove_dislike_from_user_to_playlist(user_id,playlist_id)
    
    async def add_love_from_user_to_playlist(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for add_love_from_user_to_playlist
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        return await self._repository.add_love_from_user_to_playlist(user_id,playlist_id)
    
    async def remove_love_from_user_to_playlist(self,user_id:str,playlist_id:str) -> bool:
        '''
        Docstring for remove_love_from_user_to_playlist
        
        :type user_id: str
        :type playlist_id: str
        :rtype: bool
        '''
        return await self._repository.remove_love_from_user_to_playlist(user_id,playlist_id)

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
    
    async def search_playlist_by_name(self,text:str,limit:int=100,skip:int=0) -> Sequence[PlaylistSchema]:
        '''
        Docstring for search_playlist_by_name
        
        :type text: str
        :type limit: int
        :type skip: int
        :rtype: Sequence[PlaylistSchema]
        '''
        playlists = await self._repository.search_playlists_by_name(text,limit,skip)
        return [await self._to_schema(playlist) for playlist in playlists if playlist] # type: ignore
    
    async def search_playlists_by_author_name(self,text:str,limit:int=100,skip:int=0) -> Sequence[PlaylistSchema]:
        '''
        Docstring for search_playlists_by_author_name
        
        :type text: str
        :type limit: int
        :type skip: int
        :rtype: Sequence[PlaylistSchema]
        '''
        playlists = await self._repository.search_playlists_by_author_name(text,limit,skip)
        return [await self._to_schema(playlist) for playlist in playlists if playlist] # type: ignore
    
    async def search_playlists_by_text(self,text:str,limit:int=100,skip:int=0) -> Sequence[PlaylistSchema]:
        '''
        Docstring for search_playlists_by_text
        
        :type text: str
        :type limit: int
        :type skipt: int
        :rtype: Sequence[PlaylistSchema]
        '''
        playlists = await self._repository.search_playlists_by_text(text,limit,skip)
        return [await self._to_schema(playlist) for playlist in playlists if playlist] # type: ignore

    async def search_playlists(
        self,
        text:str,
        limit:int=100,
        skip:int=0,
        search_mode:PlaylistSearchMode=PlaylistSearchMode.BOTH
    ) -> Sequence[PlaylistSchema]:
        '''
        Docstring for search_playlists_by_text
        
        :type text: str
        :type limit: int
        :type skip: int
        :type search_mode: PlaylistSearchMode
        :rtype: Sequence[PlaylistSchema]
        '''

        match search_mode:
            case PlaylistSearchMode.BOTH:
                return await self.search_playlists_by_text(text,limit,skip)
            case PlaylistSearchMode.BY_NAME:
                return await self.search_playlist_by_name(text,limit,skip)
            case PlaylistSearchMode.BY_AUTHOR:
                return await self.search_playlists_by_author_name(text,limit,skip)