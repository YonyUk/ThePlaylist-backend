from typing import Sequence
from pathlib import Path
from fastapi import APIRouter,HTTPException,status,Depends,Query,UploadFile,File,Form
from schemas import TrackDownloadSchema,TrackSchema,TrackUploadSchema,TrakUpdateSchema,UserSchema
from services import TrackService,get_track_service,get_current_user
from settings import ENVIRONMENT

router = APIRouter(prefix='/tracks',tags=['tracks'])

@router.post(
    '/upload',
    status_code=status.HTTP_201_CREATED,
    response_model=TrackSchema
)
async def upload_track(
    track_name:str,
    author_name:str,
    data:UploadFile = File(...),
    current_user:UserSchema=Depends(get_current_user),
    track_service:TrackService=Depends(get_track_service)
):
    if not data.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'The file does not have a valid filename'
        )
    extension = Path(data.filename).suffix
    track = TrackUploadSchema(name=f'{track_name}{extension}',author_name=author_name)
    track_data = await data.read()
    return await track_service.create(track,data=track_data)

@router.get(
    '',
    status_code=status.HTTP_200_OK,
    response_model=Sequence[TrackSchema]
)
async def get_tracks(
    page:int=Query(0,description='page of results',ge=0),
    limit:int=Query(1,description='limit of results',ge=1),
    service:TrackService=Depends(get_track_service)
):
    return await service.get(
        limit,
        page*ENVIRONMENT.PAGE_SIZE
    )

@router.get(
    '/{track_id}',
    response_model=TrackSchema,
    status_code=status.HTTP_200_OK
)
async def get_track(
    track_id:str,
    service:TrackService=Depends(get_track_service)
):
    db_track = await service.get_by_id(track_id)
    if not db_track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No track with id "{track_id}" was found'
        )
    return db_track

@router.get(
    '/download/{track_id}',
    response_model=TrackDownloadSchema,
    status_code=status.HTTP_200_OK
)
async def get_track_url(
    track_id:str,
    service:TrackService=Depends(get_track_service)
):
    db_track = await service.get_track_url(track_id)
    if not db_track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No track with id "{track_id}" was found'
        )
    return db_track