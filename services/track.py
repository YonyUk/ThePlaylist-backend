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
        super().__init__(Track, TrackSchema,repository, exclude_fields, exclude_unset)
    
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