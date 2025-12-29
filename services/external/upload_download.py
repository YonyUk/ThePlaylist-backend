from hashlib import sha256
import mimetypes
import datetime
import asyncio
import logging
from io import IOBase
from pathlib import Path
from typing import Callable, Tuple
from b2sdk.v2 import InMemoryAccountInfo,B2Api,UploadSourceBytes,UploadSourceStream,FileVersion
from b2sdk.v2.exception import B2ConnectionError,B2Error,B2RequestTimeout
import filetype
import magic
import mimetypes
from schemas import TrackUploadedSchema,TrackSchema,TrackDownloadSchema,TrackUploadSchema
from settings import ENVIRONMENT
from fastapi import HTTPException, UploadFile,status
from .circuit_breaker import AsyncCircuitBreaker

logger = logging.getLogger(__name__)

circuit = AsyncCircuitBreaker(60,100)

class FileValidationResult:
    
    def __init__(self,size:int,content_hash:str,extension:str):
        self._size = size
        self._hash = content_hash
        self._extension = extension

    @property
    def size(self) -> int:
        return self._size
    
    @property
    def hash(self) -> str:
        return self._hash
    
    @property
    def extension(self) -> str:
        return self._extension

class BackBlazeB2Service:
    def __init__(self):
        '''
        Docstring for __init__
        
        service to use BackBlazeB2 cloud-storage platform
        '''
        mimetypes.add_type("audio/x-m4a",'.m4a')
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
            logger.error(f'Can not acces to backblazeb2 service: {ex}')
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail='Can not connect to backblazeb2 service'
            )
        
    async def _validate_file(self,data:UploadFile) -> FileValidationResult:
        '''
        Docstring for validate_file
        
        :type data: UploadFile
        '''
        if not data.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'The file does not have a valid filename'
            )
        
        # gets the file size
        data.file.seek(0,2)
        file_size = data.file.tell()
        data.file.seek(0)
    
        hasher = sha256()
        chunks = []
        chunk = await data.read(ENVIRONMENT.CHUNK_SIZE)
        while chunk:
            chunks.append(chunk)
            hasher.update(chunk)
            chunk = await data.read(ENVIRONMENT.CHUNK_SIZE)

        await data.seek(0)

        content_hash = hasher.hexdigest()

        extension = Path(data.filename).suffix
        
        file_header = await data.read(2048)
        await data.seek(0)
        mime_type = magic.from_buffer(b''.join(chunks),mime=True)
        if not mime_type in ENVIRONMENT.ALLOWED_TRACKS_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f'Unsupported type file: {mime_type}. Allowed :{ENVIRONMENT.ALLOWED_TRACKS_MIME_TYPES}'
            )
        
        kind = filetype.guess(file_header)
        if not kind:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail='The file is corrupted'
            )
        
        if not f'.{kind.extension}' == extension:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f'The extension of your file is "{extension}" what is different from the content type ".{kind.extension}" detected'
            )
        if not f'.{kind.extension}' == mimetypes.guess_extension(mime_type):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f'The expected extension for the mime type of the given file does not matchs with the content, rejected for security'
            )
        return FileValidationResult(
            file_size,
            content_hash,
            extension
        )

    async def upload_file(self,data: UploadFile,track_name:str) -> Tuple[TrackUploadedSchema,str]:
        return await circuit.execute(lambda:self._internal_upload_file(data,track_name))

    async def get_file(self,track:TrackSchema) -> TrackDownloadSchema:
        return await circuit.execute(lambda:self._internal_get_file(track))
    
    async def rename_file(self,file_id:str,file_name:str,new_file_name:str) -> TrackUploadedSchema:
        return await circuit.execute(lambda:self._internal_rename_file(file_id,file_name,new_file_name))

    async def remove_file(self,file_id:str,file_name:str) -> bool:
        return await circuit.execute(lambda:self._internal_remove_file(file_id,file_name))

    async def _internal_upload_file(self,data: UploadFile,track_name:str) -> Tuple[TrackUploadedSchema,str]:
        validation_result = await self._validate_file(data)

        if validation_result.size > ENVIRONMENT.MAX_TRACK_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'File too large. Maximum size allowed is {ENVIRONMENT.MAX_TRACK_SIZE // 1024*1024 }MB'
            )

        try:
            data.file.seek(0)

            if validation_result.size < ENVIRONMENT.STREAMING_THRESHOLD:
                track_data = await data.read()
                cloud_response = await self._upload_file(track_data,f'{track_name}{validation_result.extension}')
            else:
                def stream_opener():
                    return data.file

                cloud_response = await self._upload_file_streaming(
                    stream_opener=stream_opener, # type: ignore
                    file_name=f'{track_name}{validation_result.extension}',
                    file_size=validation_result.size
                )            
            return cloud_response,validation_result.hash
        except HTTPException:
            raise
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='An unexpected error has ocurred'
            )

    async def _upload_file_streaming(
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
            uploaded_file:FileVersion = await asyncio.to_thread(
                lambda:self._bucket.upload(
                upload_source=upload_source,
                file_name=file_name,
                content_type=content_type
            ))

            return TrackUploadedSchema(
                id=uploaded_file.id_,
                filename=uploaded_file.file_name,
                content_type=str(uploaded_file.content_type),
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
                detail=f'Connection failed'
            )
        except B2Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'An unexpected error has ocurred'
            )

    async def _upload_file(
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
            uploaded_file:FileVersion = await asyncio.to_thread(
                lambda:self._bucket.upload(
                upload_source=upload_source,
                file_name=file_name,
                content_type=content_type
            ))

            return TrackUploadedSchema(
                id=uploaded_file.id_,
                filename=uploaded_file.file_name,
                content_type=str(uploaded_file.content_type),
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
                detail=f'Connection failed'
            )
        except B2Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'An unexpected error has ocurred'
            )
        
    async def _internal_get_file(self,track:TrackSchema) -> TrackDownloadSchema:
        '''
        Docstring for get_file_by_id
        
        :type track: TrackSchema
        :rtype: TrackDownloadSchema
        '''
        try:
            file = await asyncio.to_thread(
                lambda:self._api.get_file_info(track.file_id)
            )
            authorization_token = await asyncio.to_thread(
                lambda:self._bucket.get_download_authorization(
                file_name_prefix=file.file_name,
                valid_duration_in_seconds=ENVIRONMENT.BACKBLAZEB2_URL_LIFETIME
            ))
            url = await asyncio.to_thread(
                lambda:self._api.get_download_url_for_file_name(self._bucket.name,file.file_name)
            )
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
                detail=f'Connection failed'
            )
        except B2Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'An unexpected error has ocurred'
            )
    
    async def _internal_rename_file(self,file_id:str,file_name:str,new_file_name:str) -> TrackUploadedSchema:
        '''
        Docstring for rename_file
        
        :type file_id: str
        :type file_name: str
        :type new_file_name: str
        :rtype: TrackUploadedSchema
        '''
        try:
            new_file = await asyncio.to_thread(
                lambda:self._bucket.copy(
                file_id=file_id,
                new_file_name=new_file_name
            ))
            await asyncio.to_thread(
                lambda:self._api.delete_file_version(file_id,file_name,True)
            )
            return TrackUploadedSchema(
                id=new_file.id_,
                filename=new_file.file_name,
                content_type=str(new_file.content_type),
                content_sha1=new_file.content_sha1,
                size=new_file.size,
                uploaded_at=datetime.datetime.fromtimestamp(
                    new_file.upload_timestamp / 1000,
                    datetime.UTC
                )
            )
        except B2RequestTimeout as e:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail='The upgrade process took too long to complete'
            )
        except B2ConnectionError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Connection failed'
            )
        except B2Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'An unexpected error has ocurred'
            )

    async def _internal_remove_file(self,file_id:str,file_name:str) -> bool:
        '''
        Docstring for remove_file
        
        :type file_id: str
        :type file_name: str
        :rtype: bool
        '''
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda:self._api.delete_file_version(file_id,file_name,True)
            )
            return True
        except B2RequestTimeout as e:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail='The deleting process took too long to complete'
            )
        except B2ConnectionError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Connection failed'
            )
        except B2Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'An unexpected error has ocurred'
            )