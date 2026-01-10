from typing import List
from pydantic import BaseModel, field_validator

class TrackBaseSchema(BaseModel):
    '''
    Docstring for TrackBaseSchema
    
    base schema for 'Track' entity
    '''
    name:str
    author_name:str

class TrackPrivateUpdateSchema(TrackBaseSchema):
    '''
    Docstring for TrackPrivateUpdateSchema
    
    private update data schema
    '''

class TrackUploadSchema(TrackBaseSchema):
    '''
    Docstring for TrackUploadSchema
    
    schema for 'Track' upload operation
    '''
    file_id:str
    content_hash:str

class TrackUpdateSchema(BaseModel):
    '''
    Docstring for TrakUpdateSchema
    
    schema for 'Track' entity updates
    '''
    likes:int
    dislikes:int
    loves:int
    plays:int

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
    uploaded_by:str
    file_id:str
    content_hash:str
    playlists:List[str]

    @field_validator('playlists',mode='before')
    @classmethod
    def extract_playlists_ids(cls,l):
        if not l:
            return []
        if isinstance(l,list):
            if hasattr(l[0],'__table__'): # if is an SQLAlchemy model
                return [str(item.id) for item in l]
            elif isinstance(l[0],dict):
                return [item['id'] for item in l]
        return l

    class Config:
        from_attributes = True
        exclude = {'playlist_objects'}

class TrackDownloadSchema(TrackBaseSchema):
    '''
    Docstring for TrackDownloadSchema
    
    schema to download 'Track'
    '''
    id:str
    size:int
    url:str
    expires:int

    class Config:
        from_attributes = True