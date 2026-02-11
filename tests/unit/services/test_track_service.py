import pytest

from services import TrackService
from schemas import (
    TrackSchema,
    TrackUploadSchema,
    TrackUpdateSchema,
    TrackPrivateUpdateSchema
)

class TestTrackService:

    def assert_tracks_equals(self,track_result:TrackSchema | None,track_base:TrackSchema):
        assert track_result is not None
        assert track_result.author_name == track_base.author_name
        assert track_result.content_hash == track_base.content_hash
        assert track_result.dislikes == track_base.dislikes
        assert track_result.file_id == track_base.file_id
        assert track_result.id == track_base.id
        assert track_result.likes == track_base.likes
        assert track_result.loves == track_base.loves
        assert track_result.name == track_base.name
        
        playlists_result = set(track_result.playlists)
        playlists_base = set(track_base.playlists)

        assert len(playlists_result.difference(playlists_base)) == 0
        assert len(playlists_base.difference(playlists_result)) == 0
        assert track_result.plays == track_base.plays
        assert track_result.size == track_base.size
        assert track_result.uploaded_by == track_base.uploaded_by

    @pytest.fixture
    def user_id(self):
        return 'user_id'

    @pytest.fixture
    def track_upload(self):
        return TrackUploadSchema(
            file_id='file_id',
            name='my track',
            author_name='me',
            content_hash='content_hash'
        )

    @pytest.fixture
    def db_track(self,track_upload):
        return TrackSchema(
            id='track_id',
            file_id=track_upload.file_id,
            content_hash=track_upload.content_hash,
            name=track_upload.name,
            author_name=track_upload.author_name,
            size=10,
            likes=0,
            dislikes=0,
            loves=0,
            plays=0,
            uploaded_by='me',
            playlists=[]
        )

    @pytest.fixture
    def track_update(self):
        return TrackUpdateSchema(
            likes=1,
            dislikes=1,
            loves=1,
            plays=1
        )

    @pytest.fixture
    def track_updated(self,db_track,track_update):
        return TrackSchema(
            id=db_track.id,
            file_id=db_track.file_id,
            content_hash=db_track.content_hash,
            uploaded_by=db_track.uploaded_by,
            name=db_track.name,
            author_name=db_track.author_name,
            size=db_track.size,
            likes=track_update.likes,
            dislikes=track_update.dislikes,
            loves=track_update.loves,
            plays=track_update.plays,
            playlists=db_track.playlists
        )

    @pytest.fixture
    def track_private_update(self):
        return TrackPrivateUpdateSchema(
            name='new name',
            author_name='new description'
        )

    @pytest.fixture
    def track_private_updated(self,db_track,track_private_update):
        return TrackSchema(
            id=db_track.id,
            file_id=db_track.file_id,
            content_hash=db_track.content_hash,
            uploaded_by=db_track.uploaded_by,
            name=track_private_update.name,
            author_name=track_private_update.author_name,
            likes=db_track.likes,
            dislikes=db_track.dislikes,
            loves=db_track.loves,
            plays=db_track.plays,
            playlists=db_track.playlists,
            size=db_track.size
        )

    @pytest.mark.asyncio
    async def test_create_track(
        self,
        mocked_track_repository,
        db_track,
        track_upload
    ):
        mocked_track_repository.create.return_value = db_track

        service = TrackService(mocked_track_repository)

        track = await service.create(track_upload)

        mocked_track_repository.create.assert_awaited_once()
        self.assert_tracks_equals(track,db_track)
    
    @pytest.mark.asyncio
    async def test_get_track(
        self,
        mocked_track_repository,
        db_track
    ):
        mocked_track_repository.get_by_id.return_value = db_track

        service = TrackService(mocked_track_repository)

        track = await service.get_by_id(db_track.id)

        mocked_track_repository.get_by_id.assert_awaited_once_with(db_track.id)
        self.assert_tracks_equals(track,db_track)
    
    @pytest.mark.asyncio
    async def test_update_track(
        self,
        mocked_track_repository,
        db_track,
        track_update,
        track_updated
    ):
        mocked_track_repository.get_by_id.return_value = db_track
        mocked_track_repository.update.return_value = track_updated

        service = TrackService(mocked_track_repository)

        track = await service.update(db_track.id,track_update)

        mocked_track_repository.get_by_id.assert_awaited_once_with(db_track.id)
        mocked_track_repository.update.assert_awaited_once()
        self.assert_tracks_equals(track,track_updated)
    
    @pytest.mark.asyncio
    async def test_private_update_track(
        self,
        mocked_track_repository,
        db_track,
        track_private_update,
        track_private_updated
    ):
        mocked_track_repository.get_by_id.return_value = db_track
        mocked_track_repository.update.return_value = track_private_updated

        service = TrackService(mocked_track_repository)

        track = await service.private_update(db_track.id,track_private_update)

        mocked_track_repository.get_by_id.assert_awaited_once_with(db_track.id)
        mocked_track_repository.update.assert_awaited_once()
        self.assert_tracks_equals(track,track_private_updated)
    
    @pytest.mark.asyncio
    async def test_delete_track(
        self,
        mocked_track_repository,
        db_track
    ):
        mocked_track_repository.delete.return_value = True

        service = TrackService(mocked_track_repository)

        result = await service.delete(db_track.id)

        mocked_track_repository.delete.assert_awaited_once_with(db_track.id)
        assert result == True
    
    @pytest.mark.parametrize('reaction_type,method_name',[
        ('like','add_like_from_user_to_track'),
        ('dislike','add_dislike_from_user_to_track'),
        ('love','add_love_from_user_to_track')
    ])
    async def test_add_reactions_from_user_to_track(
        self,
        reaction_type,
        method_name,
        mocked_track_repository,
        db_track,
        user_id
    ):
        match reaction_type:
            case 'like':
                mocked_track_repository.add_like_from_user_to_track.return_value = True
            case 'dislike':
                mocked_track_repository.add_dislike_from_user_to_track.return_value = True
            case 'love':
                mocked_track_repository.add_love_from_user_to_track.return_value = True
            
        service = TrackService(mocked_track_repository)
        method = getattr(service,method_name)
        result = await method(user_id,db_track.id)

        match reaction_type:
            case 'like':
                mocked_track_repository.add_like_from_user_to_track.assert_awaited_once_with(
                    user_id,
                    db_track.id
                )
            case 'dislike':
                mocked_track_repository.add_dislike_from_user_to_track.assert_awaited_once_with(
                    user_id,
                    db_track.id
                )
            case 'love':
                mocked_track_repository.add_love_from_user_to_track.assert_awaited_once_with(
                    user_id,
                    db_track.id
                )
        
        assert result == True
    
    @pytest.mark.parametrize('reaction_type,method_name',[
        ('like','remove_like_from_user_to_track'),
        ('dislike','remove_dislike_from_user_to_track'),
        ('love','remove_love_from_user_to_track')
    ])
    async def test_remove_reactions_from_user_to_track(
        self,
        reaction_type,
        method_name,
        mocked_track_repository,
        db_track,
        user_id
    ):
        match reaction_type:
            case 'like':
                mocked_track_repository.remove_like_from_user_to_track.return_value = True
            case 'dislike':
                mocked_track_repository.remove_dislike_from_user_to_track.return_value = True
            case 'love':
                mocked_track_repository.remove_love_from_user_to_track.return_value = True
            
        service = TrackService(mocked_track_repository)
        method = getattr(service,method_name)
        result = await method(user_id,db_track.id)

        match reaction_type:
            case 'like':
                mocked_track_repository.remove_like_from_user_to_track.assert_awaited_once_with(
                    user_id,
                    db_track.id
                )
            case 'dislike':
                mocked_track_repository.remove_dislike_from_user_to_track.assert_awaited_once_with(
                    user_id,
                    db_track.id
                )
            case 'love':
                mocked_track_repository.remove_love_from_user_to_track.assert_awaited_once_with(
                    user_id,
                    db_track.id
                )
        
        assert result == True