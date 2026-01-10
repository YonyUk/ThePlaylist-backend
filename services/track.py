from repositories import TrackRepository
from models import Track
from schemas import TrackUploadSchema,TrackUpdateSchema,TrackSchema,TrackPrivateUpdateSchema
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