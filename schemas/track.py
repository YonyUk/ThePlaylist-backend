from typing import List
from pydantic import BaseModel

class TrackBaseSchema(BaseModel):
    '''
    Docstring for TrackBaseSchema
    
    base schema for 'Track' entity
    '''
    name:str
    author_name:str

class TrackUploadSchema(TrackBaseSchema):
    '''
    Docstring for TrackUploadSchema
    
    schema for 'Track' upload operation
    '''

class TrakUpdateSchema(TrackBaseSchema):
    '''
    Docstring for TrakUpdateSchema
    
    schema for 'Track' entity updates
    '''

class TrackSchema(TrackBaseSchema):
    '''
    Docstring for TrackSchema
    
    schema for 'Track' entity
    '''
    id:str
    size:int
    likes:int
    dislikes:int
    loves:int
    plays:int
    playlists:List[str]

    class Config:
        from_attributes = True

class TrackDownloadSchema(TrackBaseSchema):
    '''
    Docstring for TrackDownloadSchema
    
    schema to download 'Track'
    '''
    id:str
    size:int
    url:str

    class Config:
        from_attributes = True