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