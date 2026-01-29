from typing import Sequence
from repositories import TrackRepository
from models import Track
from schemas import (
    TrackUploadSchema,
    TrackUpdateSchema,
    TrackSchema,
    TrackPrivateUpdateSchema,
    ExistencialQuerySchema
)
from .service import Service

from enum import StrEnum

class SearchMode(StrEnum):
    BY_NAME = 'by name'
    BY_AUTHOR = 'by author'
    BOTH = 'both'

class TrackService(Service[
    Track,
    TrackRepository,
    TrackUploadSchema,
    TrackUpdateSchema,
    TrackSchema
]):
    def __init__(self, repository: TrackRepository, exclude_fields: set = set(), exclude_unset: bool = True):
        super().__init__(Track, TrackSchema,repository, exclude_fields, exclude_unset)
    
    async def private_update(self,id:str,update_data:TrackPrivateUpdateSchema,**extra_fields) -> TrackSchema | None:
        '''
        Docstring for private_update

        updates sensible data related to the track that only the owner can modify
        
        :type id: str
        :type udpate_data: TrackPrivateUpdateSchema
        :rtype: TrackSchema
        '''
        db_instance = await self._repository.get_by_id(id)
        if not db_instance:
            return None
        update_instance = await self._get_instance(**{
            **update_data.model_dump(
                exclude=self._exclude_fields,
                exclude_unset=self._exclude_unset
            ),
            **extra_fields,
            **{
                'id':id
            }
        })
        result = await self._repository.update(id,update_instance)
        return await self._to_schema(result)
    
    async def liked_by(self,user_id:str,track_id:str) -> ExistencialQuerySchema:
        '''
        Docstring for liked_by
        
        :type user_id: str
        :type track_id: str
        :rtype: bool
        '''

        result = await self._repository.liked_by(user_id,track_id)
        return ExistencialQuerySchema(result=result)
    
    async def disliked_by(self,user_id:str,track_id:str) -> ExistencialQuerySchema:
        '''
        Docstring for disliked_by
        
        :type user_id: str
        :type track_id: str
        :rtype: ExistencialQuerySchema
        '''
        result = await self._repository.disliked_by(user_id,track_id)
        return ExistencialQuerySchema(result=result)
    
    async def loved_by(self,user_id:str,track_id:str) -> ExistencialQuerySchema:
        '''
        Docstring for loved_by
        
        :type user_id: str
        :type track_id: str
        :rtype: ExistencialQuerySchema
        '''
        result = await self._repository.loved_by(user_id,track_id)
        return ExistencialQuerySchema(result=result)

    async def add_like_from_user_to_track(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for add_like_from_user_to_track

        Adds a like from the given user

        :type user_id: str
        :type track_id: str
        :rtype: VoidResultOperationSchema
        '''
        return await self._repository.add_like_from_user_to_track(user_id,track_id)
    
    async def remove_like_from_user_to_track(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for remove_like_from_user_to_track
        
        Removes a like from the given user

        :type user_id: str
        :type track_id: str
        :rtype: VoidResultOperationSchema
        '''
        return await self._repository.remove_like_from_user_to_track(user_id,track_id)
    
    async def add_dislike_from_user_to_track(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for add_dislike_from_user_to_track

        Adds a dislike from the given user
                
        :type user_id: str
        :type track_id: str
        :rtype: bool
        '''
        return await self._repository.add_dislike_from_user_to_track(user_id,track_id)
    
    async def remove_dislike_from_user_to_track(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for remove_dislike_from_user_to_track

        Remove a dislike from the given user
                
        :type user_id: str
        :type track_id: str
        :rtype: bool
        '''
        return await self._repository.remove_dislike_from_user_to_track(user_id,track_id)
    
    async def add_love_from_user_to_track(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for add_love_from_user_to_track

        Adds a love from the given user
                
        :type user_id: str
        :type track_id: str
        :rtype: bool
        '''
        return await self._repository.add_love_from_user_to_track(user_id,track_id)
    
    async def remove_love_from_user_to_track(self,user_id:str,track_id:str) -> bool:
        '''
        Docstring for remove_love_from_user_to_track

        Remove a love from the given user
                
        :type user_id: str
        :type track_str: str
        :rtype: bool
        '''
        return await self._repository.remove_love_from_user_to_track(user_id,track_id)
    
    async def get_tracks_uploaded_by(self,user_id:str,limit:int=100,skip:int=0) -> Sequence[TrackSchema]:
        '''
        Docstring for get_tracks_uploaded_by
        
        :type user_id: str
        :type limit: int
        :param skip: limit of results per query
        :type skip: number of register to jump
        :rtype: Sequence[TrackSchema]
        '''
        tracks = await self._repository.get_tracks_uploaded_by(user_id,limit,skip)
        return [await self._to_schema(track) for track in tracks if track] # type: ignore
    
    async def get_tracks_with_name_like(self,text:str,limit:int=100,skip:int=0) -> Sequence[TrackSchema]:
        '''
        Docstring for get_tracks_with_name_like
        
        :type text: str
        :param limit: limit of results per query
        :type limit: int
        :param skip: number of registers to jump
        :type skip: int
        :rtype: Sequence[TrackSchema]
        '''
        tracks = await self._repository.get_tracks_with_name_like(text,limit,skip)
        return [await self._to_schema(track) for track in tracks if track] # type: ignore
    
    async def get_tracks_with_author_name_like(self,text:str,limit:int=100,skip:int=0) -> Sequence[TrackSchema]:
        '''
        Docstring for get_tracks_with_author_name_like
        
        :type text: str
        :type limit: int
        :type skip: int
        :rtype: Sequence[TrackSchema]
        '''
        tracks = await self._repository.get_tracks_with_author_name_like(text,limit,skip)
        return [await self._to_schema(track) for track in tracks if track] # type: ignore

    async def get_tracks_from_user_with_name_like(
        self,
        user_id:str,
        text:str,
        limit:int=100,
        skip:int=0
    ) -> Sequence[TrackSchema]:
        '''
        Docstring for get_tracks_from_user_with_name_like
        
        :type user_id: str
        :type text: str
        :param limit: limit of results per query
        :type limit: int
        :param skip: number of registers to jump
        :type skip: int
        :rtype: Sequence[TrackSchema]
        '''
        tracks = await self._repository.get_tracks_from_user_with_name_like(
            user_id,
            text,
            limit,
            skip
        )
        return [await self._to_schema(track) for track in tracks if track] # type: ignore
    
    async def get_tracks_from_user_with_author_name_like(
        self,
        user_id:str,
        text:str,
        limit:int=100,
        skip:int=0
    ) -> Sequence[TrackSchema]:
        '''
        Docstring for get_tracks_from_user_with_author_name_like
        
        :type user_id: str
        :type text: str
        :type limit: int
        :type skip: int
        :rtype: Sequence[TrackSchema]
        '''
        tracks = await self._repository.get_tracks_from_user_with_author_name_like(
            user_id,
            text,limit,
            skip
        )
        return [await self._to_schema(track) for track in tracks if track] # type: ignore

    async def get_tracks_on_playlist(self,playlist_id:str,limit:int=100,skip:int=0) -> Sequence[TrackSchema]:
        '''
        Docstring for get_tracks_on_playlist
        
        :type playlist_id: str
        :rtype: Sequence[TrackSchema]
        '''
        tracks = await self._repository.get_tracks_on_playlist(playlist_id,limit,skip)
        return [await self._to_schema(track) for track in tracks if track]  # type: ignore
    
    async def get_tracks_on_playlist_with_name_like(
        self,
        playlist_id:str,
        text:str,
        limit:int=100,
        skip:int=0
    ) -> Sequence[TrackSchema]:
        '''
        Docstring for get_tracks_on_playlist_with_name_like
        
        :type playlist_id: str
        :type text: str
        :type limit: int
        :type skip: int
        :rtype: Sequence[TrackSchema]
        '''
        tracks = await self._repository.get_tracks_on_playlists_with_name_like(playlist_id,text,limit,skip)
        return [await self._to_schema(track) for track in tracks if track] # type: ignore
    
    async def get_tracks_on_playlist_with_author_name_like(
        self,
        playlist_id:str,
        text:str,
        limit:int=100,
        skip:int=0
    ) -> Sequence[TrackSchema]:
        '''
        Docstring for get_tracks_on_playlist_with_author_name_like
        
        :type playlist_id: str
        :type text: str
        :type limit: int
        :type skip: int
        :rtype: Sequence[TrackSchema]
        '''
        tracks = await self._repository.get_tracks_on_playlists_with_author_name_like(playlist_id,text,limit,skip)
        return [await self._to_schema(track) for track in tracks if track] # type: ignore
    
    async def search_track_on_playlist_by_text(self,playlist_id:str,text:str,limit:int=100,skip:int=0) -> Sequence[TrackSchema]:
        '''
        Docstring for search_track_on_playlist_by_text
        
        :type playlist_id: str
        :type text: str
        :type limit: int
        :type skip: int
        :rtype: Sequence[TrackSchema]
        '''
        tracks = await self._repository.search_tracks_on_playlist_by_text(playlist_id,text,limit,skip)
        return [await self._to_schema(track) for track in tracks if track] # type: ignore
    
    async def search_tracks_by_text(self,text:str,limit:int=100,skip:int=0) -> Sequence[TrackSchema]:
        '''
        Docstring for search_tracks_by_text
        
        :type text: str
        :type limit: int
        :type skip: int
        :rtype: Sequence[TrackSchema]
        '''
        tracks = await self._repository.search_tracks_by_text(text,limit,skip)
        return [await self._to_schema(track) for track in tracks if track] # type: ignore
    
    async def search_tracks(self,text:str,limit:int=100,skip:int=0,search_mode:SearchMode=SearchMode.BOTH) -> Sequence[TrackSchema]:
        '''
        Docstring for search_tracks
        
        :type text: str
        :type limit: int
        :type skip: int
        :type search_mode: SearchMode
        :rtype: Sequence[TrackSchema]
        '''
        match search_mode:
            case SearchMode.BY_NAME:
                return await self.get_tracks_with_name_like(text,limit,skip)
            case SearchMode.BY_AUTHOR:
                return await self.get_tracks_with_author_name_like(text,limit,skip)
            case SearchMode.BOTH:
                return await self.search_tracks_by_text(text,limit,skip)
    
    async def search_tracks_on_playlist(
        self,
        playlist_id:str,
        text:str,
        limit:int=100,
        skip:int=0,
        search_mode:SearchMode=SearchMode.BOTH
    ) -> Sequence[TrackSchema]:
        '''
        Docstring for search_tracks_on_playlist
        
        :type playlist_id: str
        :type text: str
        :type limit: int
        :type skip: int
        :type search_mode: SearchMode
        :rtype: Sequence[TrackSchema]
        '''
        match search_mode:
            case SearchMode.BOTH:
                return await self.search_track_on_playlist_by_text(playlist_id,text,limit,skip)
            case SearchMode.BY_AUTHOR:
                return await self.get_tracks_on_playlist_with_author_name_like(playlist_id,text,limit,skip)
            case SearchMode.BY_NAME:
                return await self.get_tracks_on_playlist_with_name_like(playlist_id,text,limit,skip)