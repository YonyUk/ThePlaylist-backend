from typing import Sequence
from fastapi import APIRouter,HTTPException,status,Depends,Query
from schemas import (
    PlaylistCreateSchema,
    PlaylistUpdateSchema,
    PlaylistSchema,
    PlaylistPrivateUpdateSchema,
    UserSchema,
    ExistencialQuerySchema
)
from services import (
    UserService,
    PlaylistService,
    TrackService,
    PlaylistSearchMode,
    get_playlist_service,
    get_current_user,
    get_track_service,
    get_user_service
)
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
    limit:int=Query(1,description='limit of results',ge=1,le=ENVIRONMENT.MAX_LIMIT_ALLOWED),
    pattern:str=Query('',description='pattern to search'),
    search_mode:PlaylistSearchMode=Query(PlaylistSearchMode.BOTH,description='mode to search playlists'),
    service:PlaylistService=Depends(get_playlist_service)
):
    if len(pattern) != 0:
        return await service.search_playlists(pattern,limit,page*limit,search_mode)
    
    return await service.get(
        limit,
        page*limit
    )

@router.get(
    '/search/{playlist_name}',
    status_code=status.HTTP_200_OK,
    response_model=ExistencialQuerySchema
)
async def exists_playlist_with_name_from_user(
    playlist_name:str,
    user:UserSchema=Depends(get_current_user),
    service:PlaylistService=Depends(get_playlist_service)
):
    exists = await service.exists_playlist_with_name_from_user(user.id,playlist_name)
    return ExistencialQuerySchema(
        result=exists
    )
    

@router.get(
    '/search/users/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=Sequence[PlaylistSchema]
)
async def get_user_playlists(
    user_id:str,
    page:int=Query(0,description='page of results',ge=0),
    limit:int=Query(1,description='limit of results',ge=1,le=ENVIRONMENT.MAX_LIMIT_ALLOWED),
    service:PlaylistService=Depends(get_playlist_service),
    user_service:UserService=Depends(get_user_service)
):
    db_user = await user_service.get_by_id(user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No user with id {user_id} was found'
        )
    
    return await service.get_user_playlists(user_id,page*limit,limit)

@router.get(
    '/me',
    status_code=status.HTTP_200_OK,
    response_model=Sequence[PlaylistSchema]
)
async def get_my_playlists(
    page:int=Query(0,description='page of results',ge=0),
    limit:int=Query(1,description='limit of results',ge=1,le=ENVIRONMENT.MAX_LIMIT_ALLOWED),
    user:UserSchema=Depends(get_current_user),
    service:PlaylistService=Depends(get_playlist_service)
):
    return await service.get_user_playlists(user.id,page*limit,limit)

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
    update_data:PlaylistPrivateUpdateSchema,
    user:UserSchema=Depends(get_current_user),
    service:PlaylistService=Depends(get_playlist_service)
):
    db_playlist = await service.get_by_id(playlist_id)

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    
    if user.id != db_playlist.author_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Only can modify your own data'
        )
    
    db_playlist = await service.private_update(
        playlist_id,
        update_data,
        likes=db_playlist.likes,
        dislikes=db_playlist.dislikes,
        loves=db_playlist.loves,
        plays=db_playlist.plays,
        author_id=db_playlist.author_id
    )

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has ocurred while update playlist info'
        )
    
    return db_playlist

@router.get(
    '/{playlist_id}/stats/likes',
    status_code=status.HTTP_200_OK,
    response_model=ExistencialQuerySchema
)
async def liked(
    playlist_id:str,
    user:UserSchema=Depends(get_current_user),
    service:PlaylistService=Depends(get_playlist_service)
):
    db_playlist = await service.get_by_id(playlist_id)

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    
    return await service.liked_by(user.id,playlist_id)

@router.put(
    '/{playlist_id}/stats/likes',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PlaylistSchema
)
async def add_like_to_playlist(
    playlist_id:str,
    user:UserSchema=Depends(get_current_user),
    service:PlaylistService=Depends(get_playlist_service)
):
    db_playlist = await service.get_by_id(playlist_id)

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    
    result = await service.add_like_from_user_to_playlist(user.id,playlist_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='operation failed'
        )
    
    update_data:PlaylistUpdateSchema = PlaylistUpdateSchema(
        likes=db_playlist.likes + 1,
        dislikes=db_playlist.dislikes,
        loves=db_playlist.loves,
        plays=db_playlist.plays
    )

    db_playlist = await service.update(
        playlist_id,
        update_data,
        name=db_playlist.name,
        author_id=db_playlist.author_id,
        description=db_playlist.description
    )

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has ocurred while updata playlist info'
        )
    return db_playlist

@router.delete(
    '/{playlist_id}/stats/likes',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PlaylistSchema
)
async def remove_like_from_playlist(
    playlist_id:str,
    user:UserSchema=Depends(get_current_user),
    service:PlaylistService=Depends(get_playlist_service)
):
    db_playlist = await service.get_by_id(playlist_id)

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    
    result = await service.remove_like_from_user_to_playlist(user.id,playlist_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='operation failed'
        )
    
    update_data:PlaylistUpdateSchema = PlaylistUpdateSchema(
        likes=db_playlist.likes - 1,
        dislikes=db_playlist.dislikes,
        loves=db_playlist.loves,
        plays=db_playlist.plays
    )

    db_playlist = await service.update(
        playlist_id,
        update_data,
        name=db_playlist.name,
        author_id=db_playlist.author_id,
        description=db_playlist.description
    )

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has ocurred while update playlist info'
        )
    
    return db_playlist

@router.get(
    '/{playlist_id}/stats/dislikes',
    status_code=status.HTTP_200_OK,
    response_model=ExistencialQuerySchema
)
async def disliked(
    playlist_id:str,
    user:UserSchema=Depends(get_current_user),
    service:PlaylistService=Depends(get_playlist_service)
):
    db_playlist = await service.get_by_id(playlist_id)

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    
    return await service.liked_by(user.id,playlist_id)

@router.put(
    '/{playlist_id}/stats/dislikes',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PlaylistSchema
)
async def add_dislike_to_playlist(
    playlist_id:str,
    user:UserSchema=Depends(get_current_user),
    service:PlaylistService=Depends(get_playlist_service)
):
    db_playlist = await service.get_by_id(playlist_id)

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    
    result = await service.add_dislike_from_user_to_playlist(user.id,playlist_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='operation failed'
        )
    
    update_data:PlaylistUpdateSchema = PlaylistUpdateSchema(
        likes=db_playlist.likes,
        dislikes=db_playlist.dislikes + 1,
        loves=db_playlist.loves,
        plays=db_playlist.plays
    )

    db_playlist = await service.update(
        playlist_id,
        update_data,
        name=db_playlist.name,
        author_id=db_playlist.author_id,
        description=db_playlist.description
    )

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has ocurred while update playlist info'
        )
    
    return db_playlist

@router.delete(
    '/{playlist_id}/stats/dislikes',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PlaylistSchema
)
async def remove_dislike_from_playlist(
    playlist_id:str,
    user:UserSchema=Depends(get_current_user),
    service:PlaylistService=Depends(get_playlist_service)
):
    db_playlist = await service.get_by_id(playlist_id)

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    
    result = await service.remove_dislike_from_user_to_playlist(user.id,playlist_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='operation failed'
        )
    
    update_data:PlaylistUpdateSchema = PlaylistUpdateSchema(
        likes=db_playlist.likes,
        dislikes=db_playlist.dislikes - 1,
        loves=db_playlist.loves,
        plays=db_playlist.plays
    )

    db_playlist = await service.update(
        playlist_id,
        update_data,
        name=db_playlist.name,
        author_id=db_playlist.author_id,
        description=db_playlist.description
    )

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has ocurred while update playlist info'
        )
    
    return db_playlist

@router.get(
    '/{playlist_id}/stats/loves',
    status_code=status.HTTP_200_OK,
    response_model=ExistencialQuerySchema
)
async def loved(
    playlist_id:str,
    user:UserSchema=Depends(get_current_user),
    service:PlaylistService=Depends(get_playlist_service)
):
    db_playlist = await service.get_by_id(playlist_id)

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    
    return await service.liked_by(user.id,playlist_id)

@router.put(
    '/{playlist_id}/stats/loves',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PlaylistSchema
)
async def add_love_to_playlist(
    playlist_id:str,
    user:UserSchema=Depends(get_current_user),
    service:PlaylistService=Depends(get_playlist_service)
):
    db_playlist = await service.get_by_id(playlist_id)

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    
    result = await service.add_love_from_user_to_playlist(user.id,playlist_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='operation failed'
        )
    
    update_data:PlaylistUpdateSchema = PlaylistUpdateSchema(
        likes=db_playlist.likes,
        dislikes=db_playlist.dislikes,
        loves=db_playlist.loves + 1,
        plays=db_playlist.plays
    )

    db_playlist = await service.update(
        playlist_id,
        update_data,
        name=db_playlist.name,
        author_id=db_playlist.author_id,
        description=db_playlist.description
    )

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has ocurred while update playlist info'
        )
    
    return db_playlist

@router.delete(
    '/{playlist_id}/stats/loves',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PlaylistSchema
)
async def remove_love_from_playlist(
    playlist_id:str,
    user:UserSchema=Depends(get_current_user),
    service:PlaylistService=Depends(get_playlist_service)
):
    db_playlist = await service.get_by_id(playlist_id)

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    
    result = await service.remove_love_from_user_to_playlist(user.id,playlist_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='operation failed'
        )
    
    update_data:PlaylistUpdateSchema = PlaylistUpdateSchema(
        likes=db_playlist.likes,
        dislikes=db_playlist.dislikes,
        loves=db_playlist.loves - 1,
        plays=db_playlist.plays
    )

    db_playlist = await service.update(
        playlist_id,
        update_data,
        name=db_playlist.name,
        author_id=db_playlist.author_id,
        description=db_playlist.description
    )

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has ocurred while update playlist info'
        )
    
    return db_playlist

@router.put(
    '/{playlist_id}/stats/plays',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PlaylistSchema
)
async def add_play_to_playlist(
    playlist_id:str,
    service:PlaylistService=Depends(get_playlist_service)
):
    db_playlist = await service.get_by_id(playlist_id)

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    
    update_data:PlaylistUpdateSchema = PlaylistUpdateSchema(
        likes=db_playlist.likes,
        dislikes=db_playlist.dislikes,
        loves=db_playlist.loves,
        plays=db_playlist.plays + 1
    )

    db_playlist = await service.update(
        playlist_id,
        update_data,
        name=db_playlist.name,
        author_id=db_playlist.author_id,
        description=db_playlist.description
    )

    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has ocurred while update playlist info'
        )
    
    return db_playlist

@router.put(
    '/{playlist_id}/tracks',
    status_code=status.HTTP_202_ACCEPTED
)
async def add_track(
    playlist_id:str,
    track_id:str,
    service:PlaylistService=Depends(get_playlist_service),
    track_service:TrackService=Depends(get_track_service),
    current_user:UserSchema=Depends(get_current_user)
):
    db_playlist = await service.get_by_id(playlist_id)
    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    
    db_track = await track_service.get_by_id(track_id)
    if not db_track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No track with id {track_id} was found'
        )
    
    if db_playlist.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Only can add tracks to your own playlists'
        )
    
    result = await service.add_track_to_playlist(playlist_id,track_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An unexpected error has ocurred'
        )
    
    return {'message':'track added'}

@router.delete(
    '/{playlist_id}/tracks',
    status_code=status.HTTP_202_ACCEPTED
)
async def remove_track(
    playlist_id:str,
    track_id:str,
    service:PlaylistService=Depends(get_playlist_service),
    track_service:TrackService=Depends(get_track_service),
    current_user:UserSchema=Depends(get_current_user)
):
    db_playlist = await service.get_by_id(playlist_id)
    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No playlist with id {playlist_id} was found'
        )
    
    db_track = await track_service.get_by_id(track_id)
    if not db_track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No track with id {track_id} was found'
        )
    
    if db_playlist.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Only can remove tracks from your own playlists'
        )
    
    result = await service.remove_track_from_playlist(playlist_id,track_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An unexpected error has ocurred'
        )
    
    return {'message':'track removed'}

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
    
    if current_user.id != db_playlist.author_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Only can modify your own data'
        )
    
    deleted = await service.delete(playlist_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error has occurred while deleting'
        )
    return {'message':'data deleted successfully'}