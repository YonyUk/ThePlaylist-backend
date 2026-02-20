import pytest
from unittest.mock import MagicMock,AsyncMock
import os
from typing import Tuple
from fastapi import UploadFile
import datetime
import time

from services.external.upload_download import BackBlazeB2Service
from schemas import TrackSchema
from b2sdk.v2 import Bucket,B2Api,FileVersion

class TestBackBlazeB2Service:

    @pytest.fixture
    def filepath(self,track_name):
        return os.path.join(os.getcwd(),os.path.join('tests',os.path.join('tests_assets',track_name)))

    @pytest.fixture
    def file_to_upload(self,filepath,track_name):
        with open(filepath,'rb') as f:
            yield UploadFile(f,filename=track_name,size=os.stat(filepath).st_size)
    
    @pytest.fixture
    def file_size(self,file_to_upload:UploadFile):
        return file_to_upload.size
        
    @pytest.fixture
    def track_name(self):
        return 'Awaken.m4a'
    
    @pytest.fixture
    def content_type(self):
        return "audio/x-m4a"
    
    @pytest.fixture
    def bucket(self):
        bucket = MagicMock(spec=Bucket)
        bucket.configure_mock(
            name='bucket name'
        )
        return bucket
    
    @pytest.fixture
    def api(self):
        return MagicMock(spec=B2Api)
    
    @pytest.fixture
    def content_sha1(self):
        return 'sha1'

    @pytest.fixture
    def upload_timestamp(self):
        return time.time()

    @pytest.fixture
    def track_uploaded(
        self,
        track_name,
        content_type,
        content_sha1,
        file_size,
        upload_timestamp
    ):
        result = AsyncMock(spec=FileVersion)
        result.configure_mock(
            id_='file_id',
            file_name=track_name,
            content_type=content_type,
            content_sha1=content_sha1,
            size=file_size,
            upload_timestamp = upload_timestamp
        )
        return result
    
    @pytest.fixture
    def track(
        self,
        track_uploaded:FileVersion
    ):
        return TrackSchema(
            name=track_uploaded.file_name,
            author_name='me',
            id='track_id',
            size=track_uploaded.size,
            likes=0,
            dislikes=0,
            loves=0,
            plays=0,
            playlists=[],
            uploaded_by='me',
            file_id='file_id',
            content_hash='hash'
        )

    @pytest.mark.asyncio
    async def test_upload_file(
        self,
        bucket,
        track_uploaded:FileVersion,
        file_to_upload:UploadFile,
        track_name:str,
    ):
        
        def mock_upload(*args,**kwargs):
            return track_uploaded

        service = BackBlazeB2Service(True)
        bucket.upload.side_effect = mock_upload
        service._bucket = bucket
        track,_ = await service.upload_file(file_to_upload,track_name)

        bucket.upload.assert_called_once()
        assert track.id == track_uploaded.id_
        assert track.filename == track_uploaded.file_name
        assert track.content_sha1 == track_uploaded.content_sha1
        assert track.content_type == track_uploaded.content_type
        assert track.size == track_uploaded.size
        uploaded_at = datetime.datetime.fromtimestamp(
            track_uploaded.upload_timestamp / 1000,
            datetime.UTC
        )
        assert track.uploaded_at == uploaded_at
    
    @pytest.mark.asyncio
    async def test_get_file(
        self,
        track:TrackSchema,
        api,
        bucket,
        track_uploaded:FileVersion
    ):
        service = BackBlazeB2Service(True)
        bucket.get_download_authorization.return_value='authorization-token'
        api.get_file_info.return_value = track_uploaded
        api.get_download_url_for_file_name.return_value = f'http://www.theplaylist.com/{track_uploaded.file_name}'

        service._api = api
        service._bucket = bucket

        track_download = await service.get_file(track)

        bucket.get_download_authorization.assert_called_once()
        api.get_file_info.assert_called_once()
        api.get_download_url_for_file_name.assert_called_once()

        assert track_download.author_name == track.author_name
        assert track_download.name == track.name
        assert track_download.size == track.size
        assert track_download.url == f'http://www.theplaylist.com/{track_uploaded.file_name}?Authorization=authorization-token'