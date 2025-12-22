from typing import Sequence
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
    track = TrackUploadSchema(name=track_name,author_name=author_name)
    track_data = await data.read()
    return await track_service.create(track,data=track_data)

@router.get(
    '',
    status_code=status.HTTP_200_OK,
    response_model=Sequence[TrackSchema]
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