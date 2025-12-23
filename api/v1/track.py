import logging
from hashlib import sha256
from typing import Sequence
from pathlib import Path
from fastapi import APIRouter,HTTPException,status,Depends,Query,UploadFile,File
from schemas import TrackDownloadSchema,TrackSchema,TrackUploadSchema,UserSchema
from services import TrackService,get_track_service,get_current_user,BackBlazeB2Service,get_backblazeb2_service
from settings import ENVIRONMENT

logger = logging.getLogger(__name__)

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
    track_service:TrackService=Depends(get_track_service),
    cloud_service:BackBlazeB2Service=Depends(get_backblazeb2_service)
):
    if not data.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'The file does not have a valid filename'
        )
    extension = Path(data.filename).suffix
    
    # gets the file size
    data.file.seek(0,2)
    file_size = data.file.tell()
    data.file.seek(0)

    hasher = sha256()
    chunk = await data.read(ENVIRONMENT.CHUNK_SIZE)
    while chunk:
        hasher.update(chunk)
        chunk = await data.read(ENVIRONMENT.CHUNK_SIZE)
    
    content_hash = hasher.hexdigest()

    if file_size > ENVIRONMENT.MAX_TRACK_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'File too large. Maximum size allowed is {ENVIRONMENT.MAX_TRACK_SIZE // 1024*1024 }MB'
        )

    cloud_response = None
    
    try:
        if file_size < ENVIRONMENT.STREAMING_THRESHOLD:
            track_data = await data.read()
            cloud_response = await cloud_service.upload_file(track_data,track_name)
        else:
            def stream_opener():
                data.file.seek(0)
                return data.file
            
            cloud_response = await cloud_service.upload_file_streaming(
                stream_opener=stream_opener, # type: ignore
                file_name=track_name,
                file_size=file_size
            )
        
        track = TrackUploadSchema(
            name=f'{track_name}{extension}',
            author_name=author_name,
            file_id=cloud_response.id,
            content_hash=content_hash
            )
        # breakpoint()
        db_track = await track_service.create(
            track,
            size=cloud_response.size,
            uploaded_by=current_user.id
        )
        if not db_track:
            await cloud_service.remove_file(cloud_response.id,cloud_response.filename)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='The track already exists'
            )
        return db_track
    except HTTPException:
        raise
    except Exception as ex:
        if cloud_response:
            await cloud_service.remove_file(cloud_response.id,cloud_response.filename)
        logger.error(ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has ocurred'
        )
    finally:
        await data.close()

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
        page*limit
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
    service:TrackService=Depends(get_track_service),
    cloud_service:BackBlazeB2Service=Depends(get_backblazeb2_service)
):
    db_track = await service.get_by_id(track_id)
    if not db_track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No track with id "{track_id}" was found'
        )
    db_track = await cloud_service.get_file(db_track)
    if not db_track:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='The file was not found in the cloud'
        )
    return db_track

@router.delete(
    '/{track_id}',
    status_code=status.HTTP_202_ACCEPTED
)
async def delete(
    track_id:str,
    service:TrackService=Depends(get_track_service),
    current_user:UserSchema=Depends(get_current_user),
    cloud_service:BackBlazeB2Service=Depends(get_backblazeb2_service)
):
    db_track = await service.get_by_id(track_id)
    if not db_track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No track with id {track_id} was found'
        )
    if current_user.id != db_track.uploaded_by:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="a track can only be deleted by it's uploader"
        )
    cloud_deleted = await cloud_service.remove_file(track_id,db_track.name)
    if not cloud_deleted:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='The track was not deleted from cloud'
        )
    deleted = await service.delete(track_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has ocurred while deleting'
        )
    return {'message':'data deleted successfully'}