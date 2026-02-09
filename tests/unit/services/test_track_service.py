import pytest
from unittest.mock import AsyncMock, patch

from models import Track
from repositories import TrackRepository
from schemas import TrackUploadSchema,TrackPrivateUpdateSchema,TrackUpdateSchema
from services import TrackService

class TestTrackService:

    mock_repository = AsyncMock(spec=TrackRepository)
    mock_track = Track(
        id='track_id',
        file_id='file_id',
        content_hash='content_hash',
        name='track',
        author_name='track author',
        size=10,
        likes=0,
        dislikes=0,
        loves=0,
        plays=0,
        uploaded_by='uploader id'
    )

    @pytest.mark.asyncio
    async def test_private_update(self):

        mock_modified_track = Track(
            id='track_id',
            file_id='file_id',
            content_hash='content_hash',
            name='new name',
            author_name='new author',
            size=10,
            likes=0,
            dislikes=0,
            loves=0,
            plays=0,
            uploaded_by='uploader id'
        )

        update_data = TrackPrivateUpdateSchema(
            name='new name',
            author_name='new author'
        )

        self.mock_repository.get_by_id = AsyncMock()
        self.mock_repository.get_by_id.return_value = self.mock_track
        self.mock_repository.update = AsyncMock()
        self.mock_repository.update.return_value = mock_modified_track

        with patch('services.track.TrackService._get_instance',return_value=mock_modified_track):
            service = TrackService(self.mock_repository)

            track = await service.private_update(self.mock_track.id,update_data)
        
        self.mock_repository.get_by_id.assert_awaited_once_with(self.mock_track.id)
        self.mock_repository.update.assert_awaited_once_with(self.mock_track.id,mock_modified_track)

        assert track is not None
        assert track.id == mock_modified_track.id
        assert track.file_id == mock_modified_track.file_id
        assert track.content_hash == mock_modified_track.content_hash
        assert track.name == mock_modified_track.name
        assert track.author_name == mock_modified_track.author_name
        assert track.size == mock_modified_track.size
        assert track.likes == mock_modified_track.likes
        assert track.dislikes == mock_modified_track.dislikes
        assert track.loves == mock_modified_track.loves
        assert track.plays == mock_modified_track.plays
        assert track.uploaded_by == mock_modified_track.uploaded_by
    
    @pytest.mark.asyncio
    async def test_create_track(self):

        mock_create_track = TrackUploadSchema(
            name=self.mock_track.name,
            author_name=self.mock_track.author_name,
            file_id=self.mock_track.file_id,
            content_hash=self.mock_track.content_hash
        )

        self.mock_repository.create.return_value = self.mock_track

        with patch('services.track.TrackService._get_instance',return_value=self.mock_track):

            service = TrackService(self.mock_repository)

            track = await service.create(mock_create_track)

        self.mock_repository.create.assert_awaited_once_with(self.mock_track)
        assert track is not None
        assert track.id == self.mock_track.id
        assert track.file_id == self.mock_track.file_id
        assert track.content_hash == self.mock_track.content_hash
        assert track.name == self.mock_track.name
        assert track.author_name == self.mock_track.author_name
        assert track.size == self.mock_track.size
        assert track.likes == self.mock_track.likes
        assert track.dislikes == self.mock_track.dislikes
        assert track.loves == self.mock_track.loves
        assert track.plays == self.mock_track.plays
        assert track.uploaded_by == self.mock_track.uploaded_by

    @pytest.mark.asyncio
    async def test_get_track(self):

        self.mock_repository.get_by_id = AsyncMock()
        self.mock_repository.get_by_id.return_value = self.mock_track

        service = TrackService(self.mock_repository)

        track = await service.get_by_id(self.mock_track.id)

        self.mock_repository.get_by_id.assert_awaited_once_with(self.mock_track.id)

        assert track is not None
        assert track.id == self.mock_track.id
        assert track.file_id == self.mock_track.file_id
        assert track.content_hash == self.mock_track.content_hash
        assert track.name == self.mock_track.name
        assert track.author_name == self.mock_track.author_name
        assert track.size == self.mock_track.size
        assert track.likes == self.mock_track.likes
        assert track.dislikes == self.mock_track.dislikes
        assert track.loves == self.mock_track.loves
        assert track.plays == self.mock_track.plays
        assert track.uploaded_by == self.mock_track.uploaded_by
    
    @pytest.mark.asyncio
    async def test_get_tracks(self):

        self.mock_repository.get_instances = AsyncMock()
        self.mock_repository.get_instances.return_value = [self.mock_track]

        service = TrackService(self.mock_repository)

        tracks = await service.get()

        self.mock_repository.get_instances.assert_awaited_once()

        assert len(tracks) == 1
        assert tracks[0].id == self.mock_track.id
        assert tracks[0].file_id == self.mock_track.file_id
        assert tracks[0].content_hash == self.mock_track.content_hash
        assert tracks[0].name == self.mock_track.name
        assert tracks[0].author_name == self.mock_track.author_name
        assert tracks[0].size == self.mock_track.size
        assert tracks[0].likes == self.mock_track.likes
        assert tracks[0].dislikes == self.mock_track.dislikes
        assert tracks[0].loves == self.mock_track.loves
        assert tracks[0].plays == self.mock_track.plays
        assert tracks[0].uploaded_by == self.mock_track.uploaded_by
    
    @pytest.mark.asyncio
    async def test_update_track(self):
        mock_modified_track = Track(
            id='track_id',
            file_id='file_id',
            content_hash='content_hash',
            name='new name',
            author_name='new author',
            size=10,
            likes=1,
            dislikes=1,
            loves=1,
            plays=1,
            uploaded_by='uploader id'
        )

        update_data = TrackUpdateSchema(
            likes=1,
            dislikes=1,
            loves=1,
            plays=1
        )

        self.mock_repository.get_by_id = AsyncMock()
        self.mock_repository.get_by_id.return_value = self.mock_track
        self.mock_repository.update = AsyncMock()
        self.mock_repository.update.return_value = mock_modified_track

        with patch('services.track.TrackService._get_instance',return_value=mock_modified_track):
            service = TrackService(self.mock_repository)

            track = await service.update(self.mock_track.id,update_data)
        
        self.mock_repository.get_by_id.assert_awaited_once_with(self.mock_track.id)
        self.mock_repository.update.assert_awaited_once_with(self.mock_track.id,mock_modified_track)

        assert track is not None
        assert track.id == mock_modified_track.id
        assert track.file_id == mock_modified_track.file_id
        assert track.content_hash == mock_modified_track.content_hash
        assert track.name == mock_modified_track.name
        assert track.author_name == mock_modified_track.author_name
        assert track.size == mock_modified_track.size
        assert track.likes == mock_modified_track.likes
        assert track.dislikes == mock_modified_track.dislikes
        assert track.loves == mock_modified_track.loves
        assert track.plays == mock_modified_track.plays
        assert track.uploaded_by == mock_modified_track.uploaded_by