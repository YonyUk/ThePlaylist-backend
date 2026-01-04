from pydantic import BaseModel, field_validator
from typing import List, Optional,Annotated
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

class NestedTrackSchema(BaseModel):
    '''
    schema for nested 'Track' entity
    '''
    id:str
    name:str
    author_name:str

class PlaylistSchema(PlaylistUpdateSchema):
    '''
    Docstring for PlaylistSchema
    
    schema for 'Playlist' entity
    '''
    id:str
    author_id:str
    author:str
    tracks:List[NestedTrackSchema]

    @field_validator('author',mode='before')
    @classmethod
    def extract_author_name(cls,author):
        if not author:
            return ''
        if hasattr(author,'__table__'):
            return author.username
        if isinstance(author,dict):
            return author['username']
        return ''

    @field_validator('tracks',mode='before')
    @classmethod
    def extract_tracks(cls,l):
        if not l:
            return []
        if isinstance(l,list):
            if hasattr(l[0],'__table__'):
                return [
                    NestedTrackSchema(
                        id=item.id,
                        name=item.name,
                        author_name=item.author_name
                    ) for item in l
                ]
            elif isinstance(l[0],dict):
                return [
                    NestedTrackSchema(
                        id=item['id'],
                        name=item['name'],
                        author_name=item['author_name']
                        ) for item in l
                    ]
        return l
    
    class Config:
        from_attributes = True
        exclude = {'track_objects'}