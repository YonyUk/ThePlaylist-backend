from pydantic import BaseModel
import datetime

class TrackUploadedSchema(BaseModel):
    '''
    Docstring for TrackUploadedSchema
    
    schema for response of an uploaded track
    '''
    id:str
    filename:str
    content_type:str
    content_sha1:str
    size:int
    uploaded_at:datetime.datetime