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
    
    def __init__(self,repository: PlaylistRepository, exclude_fields:set=set(), exclude_unset: bool = True):
        super().__init__(Playlist, repository, exclude_fields, exclude_unset)