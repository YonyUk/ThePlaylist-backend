from pydantic import BaseModel
from typing import Optional,Annotated
from pydantic.types import StringConstraints
from settings import ENVIRONMENT

class PlaylistBaseSchema(BaseModel):
    '''
    Docstring for PlaylistBaseSchema
    
    base schema for 'Playlist' entity
    '''
    name:Annotated[
        str,
        StringConstraints(
            min_length=ENVIRONMENT.MIN_PLAYLIST_NAME_LENGTH,
            max_length=ENVIRONMENT.MAX_PLAYLIST_NAME_LENGTH
        )
    ]
    description:Annotated[
        str,
        StringConstraints(
            max_length=ENVIRONMENT.MAX_PLAYLIST_DESCRIPTION_LENGTH
        )
    ] | None

class PlaylistCreateSchema(PlaylistBaseSchema):
    '''
    Docstring for PlaylistCreateSchema
    
    schema for 'Playlist' entity creation
    '''

class PlaylistUpdateSchema(PlaylistBaseSchema):
    '''
    Docstring for PlaylistUpdateSchema
    
    schema for 'Playlist' entity updates
    '''
    likes:int
    dislikes:int
    plays:int
    loves:int

class PlaylistSchema(PlaylistUpdateSchema):
    '''
    Docstring for PlaylistSchema
    
    schema for 'Playlist' entity
    '''
    id:str
    author_id:str

    class Config:
        from_attributes = True