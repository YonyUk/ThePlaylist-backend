import mimetypes
from b2sdk.v2 import InMemoryAccountInfo,B2Api,UploadSourceBytes
from settings import ENVIRONMENT

class BackBlazeB2Service:
    def __init__(self):
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
    
    async def upload_file(self,file_data:bytes,file_name:str,content_type:str | None = None) -> dict:
        if not content_type:
            content_type,_ = mimetypes.guess_type(file_name)
            if not content_type:
                content_type = 'application/octet-stream'
            
        upload_source = UploadSourceBytes(file_data)
        uploaded_file = self._bucket.upload(
            upload_source=upload_source,
            file_name=file_name,
            content_type=content_type
        )

        authorization_token = self._bucket.get_download_authorization(
            file_name_prefix=file_name,
            valid_duration_in_seconds=60
        )
        url = self._api.get_download_url_for_file_name(self._bucket.name,file_name)

        return {
                "status": "success",
                "file_id": uploaded_file.id_,
                "file_name": uploaded_file.file_name,
                "content_type": uploaded_file.content_type,
                "content_sha1": uploaded_file.content_sha1,
                "size": uploaded_file.size,
                "upload_timestamp": uploaded_file.upload_timestamp,
                "bucket_id": uploaded_file.bucket_id
            }