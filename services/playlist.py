from repositories import PlaylistRepository
from models import Playlist
from schemas import PlaylistCreateSchema,PlaylistUpdateSchema,PlaylistSchema
from settings import ENVIRONMENT
from .service import Service

class PlaylistService(Service[
    Playlist,
    PlaylistRepository,
    PlaylistCreateSchema,
    PlaylistUpdateSchema,
    PlaylistSchema
]):
    
    def __init__(self,repository: PlaylistRepository,exclude_fields:set=set(), exclude_unset: bool = True):
        super().__init__(Playlist,PlaylistSchema,repository, exclude_fields, exclude_unset)
    
    async def add_track_to_playlist(self,playlist_id:str,track_id:str) -> bool:
        '''
        Docstring for add_track_to_playlist
        
        :type playlist_id: str
        :type track_id: str
        :rtype: bool
        '''
        return await self._repository.add_track_to_playlist(playlist_id,track_id)