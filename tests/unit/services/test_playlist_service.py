import pytest

from schemas import (
    PlaylistSchema,
    PlaylistCreateSchema,
    PlaylistUpdateSchema,
    PlaylistPrivateUpdateSchema
)
from services import PlaylistService

class TestPlaylistService:

    def assert_playlists_equals(
        self,
        playlist_result:PlaylistSchema | None,
        playlist_base:PlaylistSchema
    ):
        assert playlist_result is not None
        assert playlist_result.id == playlist_base.id
        assert playlist_result.author == playlist_base.author
        assert playlist_result.author_id == playlist_base.author_id
        assert playlist_result.name == playlist_base.name
        assert playlist_result.description == playlist_base.description
        assert playlist_result.likes == playlist_base.likes
        assert playlist_result.dislikes == playlist_base.dislikes
        assert playlist_result.loves == playlist_base.loves
        assert playlist_result.plays == playlist_base.plays
        
        result_tracks = set(map(lambda track:track.id,playlist_result.tracks))
        base_tracks = set(map(lambda track:track.id,playlist_base.tracks))

        assert len(result_tracks.difference(base_tracks)) == 0
        assert len(base_tracks.difference(result_tracks)) == 0
    
    @pytest.fixture
    def user_id(self):
        return 'user_id'
    
    @pytest.fixture
    def track_id(self):
        return 'track_id'

    @pytest.fixture
    def db_playlist(self):
        return PlaylistSchema(
            id='playlist_id',
            name='my playlist',
            likes=0,
            dislikes=0,
            loves=0,
            plays=0,
            description='description',
            author_id='author_id',
            author='author',
            tracks=[]
        )

    @pytest.fixture
    def playlist_create(self,db_playlist):
        return PlaylistCreateSchema(
            name=db_playlist.name,
            description=db_playlist.description
        )
    
    @pytest.fixture
    def playlist_update(self):
        return PlaylistUpdateSchema(
            likes=1,
            dislikes=1,
            plays=1,
            loves=1
        )
    
    @pytest.fixture
    def playlist_private_update(self):
        return PlaylistPrivateUpdateSchema(
            name='my new playlist',
            description='new description'
        )
    
    @pytest.fixture
    def playlist_updated(self,db_playlist,playlist_update):
        return PlaylistSchema(
            id=db_playlist.id,
            name=db_playlist.name,
            description=db_playlist.description,
            likes=playlist_update.likes,
            dislikes=playlist_update.dislikes,
            loves=playlist_update.loves,
            plays=playlist_update.plays,
            author=db_playlist.author,
            author_id=db_playlist.author_id,
            tracks=db_playlist.tracks
        )
    
    @pytest.fixture
    def playlist_private_updated(self,db_playlist,playlist_private_update):
        return PlaylistSchema(
            id=db_playlist.id,
            name=playlist_private_update.name,
            description=playlist_private_update.description,
            likes=db_playlist.likes,
            dislikes=db_playlist.dislikes,
            loves=db_playlist.loves,
            plays=db_playlist.plays,
            author=db_playlist.author,
            author_id=db_playlist.author_id,
            tracks=db_playlist.tracks
        )

    @pytest.mark.asyncio
    async def test_create_playlist(
        self,
        mocked_playlist_repository,
        db_playlist,
        playlist_create
    ):
        mocked_playlist_repository.create.return_value = db_playlist

        service = PlaylistService(mocked_playlist_repository)

        playlist = await service.create(playlist_create)

        mocked_playlist_repository.create.assert_awaited_once()
        self.assert_playlists_equals(playlist,db_playlist)
    
    @pytest.mark.asyncio
    async def test_get_playlist(
        self,
        mocked_playlist_repository,
        db_playlist
    ):
        mocked_playlist_repository.get_by_id.return_value = db_playlist

        service = PlaylistService(mocked_playlist_repository)

        playlist = await service.get_by_id(db_playlist.id)

        mocked_playlist_repository.get_by_id.assert_awaited_once_with(db_playlist.id)
        self.assert_playlists_equals(playlist,db_playlist)
    
    @pytest.mark.asyncio
    async def test_get_wrong_playlist(
        self,
        mocked_playlist_repository
    ):
        mocked_playlist_repository.get_by_id.return_value = None

        service = PlaylistService(mocked_playlist_repository)
        
        playlist = await service.get_by_id('wrong id')

        mocked_playlist_repository.get_by_id.assert_awaited_once_with('wrong id')
        assert playlist is None
    
    @pytest.mark.asyncio
    async def test_update_playlist(
        self,
        mocked_playlist_repository,
        db_playlist,
        playlist_update,
        playlist_updated
    ):
        mocked_playlist_repository.get_by_id.return_value = db_playlist
        mocked_playlist_repository.update.return_value = playlist_updated

        service = PlaylistService(mocked_playlist_repository)

        playlist = await service.update(db_playlist.id,playlist_update)

        mocked_playlist_repository.get_by_id.assert_awaited_once_with(db_playlist.id)
        mocked_playlist_repository.update.assert_awaited_once()
        self.assert_playlists_equals(playlist,playlist_updated)
    
    @pytest.mark.asyncio
    async def test_private_update(
        self,
        mocked_playlist_repository,
        db_playlist,
        playlist_private_update,
        playlist_private_updated
    ):
        mocked_playlist_repository.get_by_id.return_value = db_playlist
        mocked_playlist_repository.update.return_value = playlist_private_updated

        service = PlaylistService(mocked_playlist_repository)

        playlist = await service.private_update(db_playlist.id,playlist_private_update)

        mocked_playlist_repository.get_by_id.assert_awaited_once_with(db_playlist.id)
        mocked_playlist_repository.update.assert_awaited_once()
        self.assert_playlists_equals(playlist,playlist_private_updated)
    
    @pytest.mark.asyncio
    async def test_delete_playlist(
        self,
        mocked_playlist_repository,
        db_playlist
    ):
        mocked_playlist_repository.delete.return_value = True

        service = PlaylistService(mocked_playlist_repository)

        result = await service.delete(db_playlist.id)
        
        assert result == True
    
    @pytest.mark.parametrize('reaction_type,method_name',[
        ('like','add_like_from_user_to_playlist'),
        ('dislike','add_dislike_from_user_to_playlist'),
        ('love','add_love_from_user_to_playlist')
    ])
    async def test_add_reactions_from_user_to_playlist(
        self,
        reaction_type,
        method_name,
        mocked_playlist_repository,
        db_playlist,
        user_id
    ):
        match reaction_type:
            case 'like':
                mocked_playlist_repository.add_like_from_user_to_playlist.return_value = True
            
            case 'dislike':
                mocked_playlist_repository.add_dislike_from_user_to_playlist.return_value = True

            case 'love':
                mocked_playlist_repository.add_love_from_user_to_playlist.return_value = True

        service = PlaylistService(mocked_playlist_repository)

        method = getattr(service,method_name)

        result = await method(user_id,db_playlist.id)

        match reaction_type:
            case 'like':
                mocked_playlist_repository.add_like_from_user_to_playlist.assert_awaited_once_with(
                    user_id,
                    db_playlist.id
                )
            
            case 'dislike':
                mocked_playlist_repository.add_dislike_from_user_to_playlist.assert_awaited_once_with(
                    user_id,
                    db_playlist.id
                )

            case 'love':
                mocked_playlist_repository.add_love_from_user_to_playlist.assert_awaited_once_with(
                    user_id,
                    db_playlist.id
                )
        assert result == True

    @pytest.mark.parametrize('reaction_type,method_name',[
        ('like','remove_like_from_user_to_playlist'),
        ('dislike','remove_dislike_from_user_to_playlist'),
        ('love','remove_love_from_user_to_playlist')
    ])
    async def test_remove_reactions_from_user_to_playlist(
        self,
        reaction_type,
        method_name,
        mocked_playlist_repository,
        db_playlist,
        user_id
    ):
        match reaction_type:
            case 'like':
                mocked_playlist_repository.remove_like_from_user_to_playlist.return_value = True
            
            case 'dislike':
                mocked_playlist_repository.remove_dislike_from_user_to_playlist.return_value = True

            case 'love':
                mocked_playlist_repository.remove_love_from_user_to_playlist.return_value = True

        service = PlaylistService(mocked_playlist_repository)

        method = getattr(service,method_name)

        result = await method(user_id,db_playlist.id)

        match reaction_type:
            case 'like':
                mocked_playlist_repository.remove_like_from_user_to_playlist.assert_awaited_once_with(
                    user_id,
                    db_playlist.id
                )
            
            case 'dislike':
                mocked_playlist_repository.remove_dislike_from_user_to_playlist.assert_awaited_once_with(
                    user_id,
                    db_playlist.id
                )

            case 'love':
                mocked_playlist_repository.remove_love_from_user_to_playlist.assert_awaited_once_with(
                    user_id,
                    db_playlist.id
                )
        assert result == True
    
    @pytest.mark.asyncio
    async def test_add_track_to_playlist(
        self,
        mocked_playlist_repository,
        track_id,
        db_playlist
    ):
        mocked_playlist_repository.add_track_to_playlist.return_value = True

        service = PlaylistService(mocked_playlist_repository)

        result = await service.add_track_to_playlist(db_playlist.id,track_id)

        mocked_playlist_repository.add_track_to_playlist.assert_awaited_once_with(
            db_playlist.id,
            track_id
        )
        assert result == True
    
    @pytest.mark.asyncio
    async def test_remove_track_from_playlist(
        self,
        mocked_playlist_repository,
        track_id,
        db_playlist
    ):
        mocked_playlist_repository.remove_track_from_playlist.return_value = True

        service = PlaylistService(mocked_playlist_repository)

        result = await service.remove_track_from_playlist(db_playlist.id,track_id)

        mocked_playlist_repository.remove_track_from_playlist.assert_awaited_once_with(
            db_playlist.id,
            track_id
        )
        assert result == True