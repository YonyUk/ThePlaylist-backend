from typing import Sequence
from fastapi import APIRouter,HTTPException,status,Depends,Query
from schemas import TrackDownloadSchema,TrackSchema,TrackUploadSchema,TrakUpdateSchema
from services import TrackService,get_track_service,get_current_user
from settings import ENVIRONMENT

router = APIRouter(prefix='/tracks',tags=['tracks'])

@router.get(
    '',
    status_code=status.HTTP_200_OK,
    response_model=TrackSchema
)
async def get_playlists(
    page:int=Query(0,description='page of results',ge=0),
    limit:int=Query(1,description='limit of results',ge=1),
    service:TrackService=Depends(get_track_service)
):
    return await service.get(
        limit,
        page*ENVIRONMENT.PAGE_SIZE
    )