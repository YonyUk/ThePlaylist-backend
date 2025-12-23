from typing import Sequence
from fastapi import APIRouter,HTTPException,status,Depends,Query
from schemas import PlaylistCreateSchema,PlaylistUpdateSchema,PlaylistSchema,UserSchema
from services import PlaylistService,get_playlist_service,get_current_user
from settings import ENVIRONMENT

router = APIRouter(prefix='/playlists',tags=['playlists'])

@router.post(
    '/create',
    status_code=status.HTTP_201_CREATED,
    response_model=PlaylistSchema
)
async def create(
    playlist:PlaylistCreateSchema,
    current_user:UserSchema=Depends(get_current_user),
    service:PlaylistService=Depends(get_playlist_service)
):
    db_playlist = await service.create(playlist,author_id=current_user.id)
    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error while creating playlist'
        )
    return db_playlist

@router.get(
    '',
    status_code=status.HTTP_200_OK,
    response_model=Sequence[PlaylistSchema]
)
async def get_playlists(
    page:int=Query(0,description='page of results',ge=0),
    limit:int=Query(1,description='limit of results',ge=1),
    service:PlaylistService=Depends(get_playlist_service)
):
    return await service.get(
        limit,
        page*limit
    )

@router.get(
    '/{playlist_id}',
    status_code=status.HTTP_200_OK,
    response_model=PlaylistSchema
)
async def get_playlist(
    playlist_id:str,
    service:PlaylistService=Depends(get_playlist_service)
):
    db_playlist = await service.get_by_id(playlist_id)
    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    return db_playlist

@router.put(
    '/{playlist_id}',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PlaylistSchema
)
async def update(
    playlist_id:str,
    update_data:PlaylistUpdateSchema,
    current_user:UserSchema=Depends(get_current_user),
    service:PlaylistService=Depends(get_playlist_service)
):
    db_playlist = await service.get_by_id(playlist_id)
    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    if current_user.id != db_playlist.author_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Only can modify your own playlists'
        )
    db_playlist = await service.update(playlist_id,update_data)
    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has occurred while updating'
        )
    return db_playlist

@router.delete(
    '/{playlist_id}',
    status_code=status.HTTP_202_ACCEPTED
)
async def delete(
    playlist_id:str,
    service:PlaylistService=Depends(get_playlist_service),
    current_user:UserSchema=Depends(get_current_user)
):
    db_playlist = await service.get_by_id(playlist_id)
    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    deleted = await service.delete(playlist_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has occurred while deleting'
        )
    return {'message':'data deleted successfully'}