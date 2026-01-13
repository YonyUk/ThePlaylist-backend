from pydantic import BaseModel
from .user import UserCreateSchema,UserUpdateSchema,UserSchema
from .access_token import AccessTokenDataSchema,AccessTokenSchema,VerificationSchema
from .playlist import PlaylistCreateSchema,PlaylistUpdateSchema,PlaylistSchema
from .track import TrackUploadSchema,TrackUpdateSchema,TrackSchema,TrackDownloadSchema,TrackPrivateUpdateSchema
from .track_upload import TrackUploadedSchema

class ExistencialQuerySchema(BaseModel):
    '''
    Docstring for ExistenceQuerySchema

    schema for an existencial query
    '''

    result:bool

class VoidResultOperationSchema(BaseModel):
    '''
    Docstring for VoidResultQuerySchema
    
    schema for a void-result operation
    '''
    success:bool
    message:str