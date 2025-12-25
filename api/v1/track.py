import logging
import magic
import filetype
from hashlib import sha256
from typing import Sequence
from pathlib import Path
from fastapi import APIRouter,HTTPException,status,Depends,Query,UploadFile,File
from schemas import TrackDownloadSchema,TrackSchema,TrackUploadSchema,UserSchema,TrackUpdateSchema
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
    # if not data.filename:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=f'The file does not have a valid filename'
    #     )
    # extension = Path(data.filename).suffix
    
    # file_header = await data.read(2048)
    # await data.seek(0)

    # mime_type = magic.from_buffer(file_header,mime=True)
    # if not mime_type in ENVIRONMENT.ALLOWED_TRACKS_MIME_TYPES:
    #     raise HTTPException(
    #         status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    #         detail=f'Unsupported type file: {mime_type}. Allowed :{ENVIRONMENT.ALLOWED_TRACKS_MIME_TYPES}'
    #     )
    
    # kind = filetype.guess(file_header)
    # if not kind:
    #     raise HTTPException(
    #         status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #         detail='The file is corrupted'
    #     )
    
    # if not f'.{kind.extension}' == extension:
    #     raise HTTPException(
    #         status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #         detail=f'The extension of your file is "{extension}" what is different from the content type ".{kind.extension}" detected'
    #     )

    # # gets the file size
    # data.file.seek(0,2)
    # file_size = data.file.tell()
    # data.file.seek(0)

    # hasher = sha256()
    # chunks = []
    # chunk = await data.read(ENVIRONMENT.CHUNK_SIZE)
    # while chunk:
    #     chunks.append(chunk)
    #     hasher.update(chunk)
    #     chunk = await data.read(ENVIRONMENT.CHUNK_SIZE)
    
    # content_hash = hasher.hexdigest()

    # if file_size > ENVIRONMENT.MAX_TRACK_SIZE:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=f'File too large. Maximum size allowed is {ENVIRONMENT.MAX_TRACK_SIZE // 1024*1024 }MB'
    #     )

    cloud_response = None
    
    try:
        cloud_response,content_hash = await cloud_service.upload_file(data,track_name,author_name)
        track = TrackUploadSchema(
            name=cloud_response.filename,
            author_name=author_name,
            file_id=cloud_response.id,
            content_hash=content_hash
            )
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
    limit:int=Query(1,description='limit of results',ge=1,le=ENVIRONMENT.MAX_LIMIT_ALLOWED),
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
    try:
        cloud_track = await cloud_service.get_file(db_track)
    
        return TrackDownloadSchema(
            id=db_track.id,
            size=cloud_track.size,
            name=db_track.name,
            author_name=db_track.author_name,
            url=cloud_track.url
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An unexpected error has ocurred'
        )


@router.put(
    '/{track_id}',
    response_model=TrackSchema,
    status_code=status.HTTP_202_ACCEPTED
)
async def update(
    track_id:str,
    update_data:TrackUpdateSchema,
    service:TrackService=Depends(get_track_service),
    cloud_service:BackBlazeB2Service=Depends(get_backblazeb2_service),
    current_user:UserSchema=Depends(get_current_user),
):
    db_track = await service.get_by_id(track_id)
    if not db_track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No track with id "{track_id}" was found'
        )
    
    file_id = db_track.file_id
    file_name = db_track.name

    if current_user.id != db_track.uploaded_by:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Only can modify data of your uploaded tracks'
        )
    
    extension = Path(db_track.name).suffix
    cloud_response = None
    try:
        cloud_response = await cloud_service.rename_file(
            db_track.file_id,
            db_track.name,
            f'{update_data.name}{extension}'
        )

        update_data.name = f'{update_data.name}{extension}'

        db_track = await service.update(
            track_id,
            update_data,
            size=cloud_response.size,
            file_id=cloud_response.id,
            content_hash=db_track.content_hash,
            uploaded_by=current_user.id
        )
        if not db_track:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='An unexpected error has ocurred while updating track info'
            )
        return db_track
    except HTTPException:
        raise
    except Exception as e:
        if cloud_response:
            cloud_response = await cloud_service.rename_file(
                file_id,
                f'{update_data.name}{extension}',
                file_name
            )
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has ocurred'
        )


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
    cloud_deleted = await cloud_service.remove_file(db_track.file_id,db_track.name)
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