import mimetypes
import datetime
from io import IOBase
from typing import Callable
from b2sdk.v2 import InMemoryAccountInfo,B2Api,UploadSourceBytes,UploadSourceStream
from b2sdk.v2.exception import B2ConnectionError,B2Error,B2RequestTimeout
from schemas import TrackUploadedSchema,TrackSchema,TrackDownloadSchema
from settings import ENVIRONMENT
from fastapi import HTTPException,status

class BackBlazeB2Service:
    def __init__(self):
        '''
        Docstring for __init__
        
        service to use BackBlazeB2 cloud-storage platform
        '''
        try:
            self._info = InMemoryAccountInfo()
            self._api = B2Api(self._info) # type: ignore
            self._api.authorize_account(
                'production',
                ENVIRONMENT.BACKBLAZEB2_AWS_ACCESS_KEY_ID,
                ENVIRONMENT.BACKBLAZEB2_AWS_SECRET_ACCESS_KEY
            )
            self._bucket = self._api.get_bucket_by_id(
                ENVIRONMENT.BACKBLAZEB2_BUCKET_ID
            )
        except Exception as ex:
            raise RuntimeError(f'Configuration error: {ex}')
    
    async def upload_file_streaming(
        self,
        stream_opener: Callable[[],IOBase],
        file_name:str,
        file_size:int,
        content_type:str | None = None,
    ) -> TrackUploadedSchema:
        if not content_type:
            content_type,_ = mimetypes.guess_type(file_name)
            if not content_type:
                content_type = 'application/octet-stream'
        
        upload_source = UploadSourceStream(
            stream_opener=stream_opener,
            stream_length=file_size
        )

        try:
            uploaded_file = self._bucket.upload(
                upload_source=upload_source,
                file_name=file_name,
                content_type=content_type
            )

            return TrackUploadedSchema(
                id=uploaded_file.id_,
                filename=uploaded_file.file_name,
                content_type=uploaded_file.content_type,
                content_sha1=uploaded_file.content_sha1,
                size=uploaded_file.size,
                uploaded_at=datetime.datetime.fromtimestamp(
                    uploaded_file.upload_timestamp / 1000,
                    datetime.UTC
                )
            )
        except B2RequestTimeout as e:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail='The upload process took too long to complete'
            )
        except B2ConnectionError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Connection failed: {e}'
            )
        except B2Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'An unexpected error has ocurred: {e}'
            )

    async def upload_file(
        self,
        file_data:bytes,
        file_name:str,
        content_type:str | None = None
    ) -> TrackUploadedSchema:
        '''
        Docstring for upload_file
        
        :param file_data: binary data of the file to upload
        :type file_data: bytes
        :type file_name: str
        :type content_type: str | None
        :rtype: TrackUploadedSchema
        '''
        if not content_type:
            content_type,_ = mimetypes.guess_type(file_name)
            if not content_type:
                content_type = 'application/octet-stream'
            
        upload_source = UploadSourceBytes(file_data)
        try:
            uploaded_file = self._bucket.upload(
                upload_source=upload_source,
                file_name=file_name,
                content_type=content_type
            )

            return TrackUploadedSchema(
                id=uploaded_file.id_,
                filename=uploaded_file.file_name,
                content_type=uploaded_file.content_type,
                content_sha1=uploaded_file.content_sha1,
                size=uploaded_file.size,
                uploaded_at=datetime.datetime.fromtimestamp(
                    uploaded_file.upload_timestamp / 1000,
                    datetime.UTC
                )
            )
        except B2RequestTimeout as e:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail='The upload process took too long to complete'
            )
        except B2ConnectionError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Connection failed: {e}'
            )
        except B2Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'An unexpected error has ocurred: {e}'
            )
        
    async def get_file(self,track:TrackSchema) -> TrackDownloadSchema:
        '''
        Docstring for get_file_by_id
        
        :type track: TrackSchema
        :rtype: TrackDownloadSchema
        '''
        try:
            file = self._api.get_file_info(track.file_id)
            authorization_token = self._bucket.get_download_authorization(
                file_name_prefix=file.file_name,
                valid_duration_in_seconds=ENVIRONMENT.BACKBLAZEB2_URL_LIFETIME
            )
            url = self._api.get_download_url_for_file_name(self._bucket.name,file.file_name)
            return TrackDownloadSchema(
                id=track.id,
                size=track.size,
                name=file.file_name,
                author_name=track.author_name,
                url=f'{url}?Authorization={authorization_token}'
            )
        except B2RequestTimeout as e:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail='The download process took too long to complete'
            )
        except B2ConnectionError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Connection failed: {e}'
            )
        except B2Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'An unexpected error has ocurred: {e}'
            )
    
    async def remove_file(self,file_id:str,file_name:str) -> bool:
        try:
            self._api.delete_file_version(file_id,file_name,True)
            return True
        except B2RequestTimeout as e:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail='The deleting process took too long to complete'
            )
        except B2ConnectionError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Connection failed: {e}'
            )
        except B2Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'An unexpected error has ocurred: {e}'
            )