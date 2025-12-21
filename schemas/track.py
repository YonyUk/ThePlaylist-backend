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
    size:float

    class Config:
        from_attributes = True

class TrackDownloadSchema(TrackSchema):
    '''
    Docstring for TrackDownloadSchema
    
    schema to download 'Track'
    '''

    url:str