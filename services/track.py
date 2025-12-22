from fastapi import HTTPException,status
from repositories import TrackRepository
from models import Track
from schemas import TrackUploadSchema,TrakUpdateSchema,TrackSchema,TrackDownloadSchema
from .service import Service
from .external.upload_download import BackBlazeB2Service

class TrackService(Service[
    Track,
    TrackRepository,
    TrackUploadSchema,
    TrakUpdateSchema,
    TrackSchema
]):
    def __init__(self, repository: TrackRepository, exclude_fields: set = set(), exclude_unset: bool = True):
        super().__init__(Track, repository, exclude_fields, exclude_unset)
        try:
            self._bacblazeb2_service = BackBlazeB2Service()
        except:
            print('Can not setup the BackBlazeB2Service')
            self._bacblazeb2_service = None
    
    async def update(self, id: str, update_data: TrakUpdateSchema) -> TrackSchema | None:
        db_instance = await self.get_by_id(id)
        if not db_instance:
            return None
        update_instance = await self._get_instance(**{
            **update_data.model_dump(
                exclude=self._exclude_fields,
                exclude_unset=self._exclude_unset
            ),
            **{
                'id':id,
                'size':db_instance.size
            }
        })
        return await self._repository.update(id,update_instance)
    
    async def create(self, value: TrackUploadSchema, **extra_fields) -> TrackSchema | None:
        if not self._bacblazeb2_service:
            return None
        if not ('data' in extra_fields.keys() and extra_fields['data']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='no value given for the field "data"'
            )
        data = extra_fields['data']
        if not type(data) == bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='type of "data" field must be bytes'
            )
        b2_response = await self._bacblazeb2_service.upload_file(
            data,
            value.name
        )
        return await super().create(
            value,
            id=b2_response.id,
            size=b2_response.size
        )
    
    async def delete(self, id: str) -> bool:
        if not self._bacblazeb2_service:
            return False
        db_track = await self.get_by_id(id)
        if not db_track:
            return False
        deleted = await self._bacblazeb2_service.remove_file(db_track.id,db_track.name)
        if not deleted:
            return False
        return await super().delete(id)
    
    async def get_track_url(self,track_id:str) -> TrackDownloadSchema | None:
        '''
        Docstring for get_track_url
        
        :type track_id: str
        :rtype: TrackDownloadSchema | None
        '''
        if not self._bacblazeb2_service:
            return None
        db_track = await self.get_by_id(track_id)
        if not db_track:
            return None
        return await self._bacblazeb2_service.get_file_by_id(db_track)