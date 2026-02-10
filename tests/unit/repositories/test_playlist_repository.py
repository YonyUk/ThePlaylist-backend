import pytest
import pytest_asyncio
from unittest.mock import MagicMock

from models import Playlist,User,Track
from repositories import PlaylistRepository

class TestPlaylistRepository:

    def assert_has_selectinload_option(self,query):
        if hasattr(query,'_with_options') and query._with_options:
            selectinload_option = list(filter(
                lambda option: 'load' in str(option).lower(),
                query._with_options
            ))
            assert len(selectinload_option) != 0

    def assert_playlists_equals(self,playlist_result:Playlist | None,playlist_base:Playlist):
        assert playlist_result is not None
        assert playlist_result.id == playlist_base.id
        assert playlist_result.name == playlist_base.name
        assert playlist_result.description == playlist_base.description
        assert playlist_result.likes == playlist_base.likes
        assert playlist_result.dislikes == playlist_base.dislikes
        assert playlist_result.plays == playlist_base.plays
        assert playlist_result.loves == playlist_base.loves

    @pytest_asyncio.fixture
    async def db_mocked_playlist(self,db_playlist):
        playlist = MagicMock()
        playlist.id.return_value = db_playlist.id
        playlist.users_likes = MagicMock()
        playlist.users_dislikes = MagicMock()
        playlist.users_loves = MagicMock()
        playlist.tracks = MagicMock()
        return playlist

    @pytest_asyncio.fixture
    async def db_playlist(self):
        return Playlist(
            id='playlist_id',
            name='my playlist',
            likes=0,
            dislikes=0,
            loves=0,
            plays=0,
            description='description'
        )
    
    @pytest_asyncio.fixture
    async def db_update_playlist(self,db_playlist):
        return Playlist(
            id=db_playlist.id,
            name='my new playlist',
            likes=1,
            dislikes=1,
            loves=1,
            plays=1,
            description='new description'
        )

    @pytest_asyncio.fixture
    async def db_user(self):
        return User(
            id='user_id',
            username='username',
            email='user@gmail.com',
            hashed_password='hashed_password'
        )

    @pytest_asyncio.fixture
    async def db_track(self):
        return Track(
            id='track_id',
            file_id='file_id',
            content_hash='content_hash',
            name='new track',
            author_name='me',
            size='4 Mb',
            likes=0,
            dislikes=0,
            loves=0,
            plays=0,
            uploaded_by='me'
        )

    @pytest.mark.asyncio
    async def test_create_playlist(
        self,
        mocked_db,
        mocked_user_repository,
        mocked_track_repository,
        mocked_get_execute_result,
        db_playlist
    ):

        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = None

        repository = PlaylistRepository(mocked_db,mocked_track_repository,mocked_user_repository)

        playlist = await repository.create(db_playlist)

        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE playlists.id =' in query
        
        mocked_db.add.assert_called_once_with(db_playlist)
        mocked_db.commit.assert_awaited_once()
        mocked_db.refresh.assert_awaited_once_with(db_playlist)
        self.assert_playlists_equals(playlist,db_playlist)
    
    @pytest.mark.asyncio
    async def test_get_playlist(
        self,
        mocked_db,
        mocked_user_repository,
        mocked_track_repository,
        mocked_get_execute_result,
        db_playlist
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = db_playlist

        repository = PlaylistRepository(mocked_db,mocked_track_repository,mocked_user_repository)

        playlist = await repository.get_by_id(db_playlist.id)

        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE playlists.id =' in query
        self.assert_playlists_equals(playlist,db_playlist)
    
    @pytest.mark.asyncio
    async def test_get_wrong_playlist(
        self,
        mocked_db,
        mocked_user_repository,
        mocked_track_repository,
        mocked_get_execute_result
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = None

        repository = PlaylistRepository(mocked_db,mocked_track_repository,mocked_user_repository)

        playlist = await repository.get_by_id('wrong id')

        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE playlists.id =' in query
        assert playlist is None

    @pytest.mark.asyncio
    async def test_update_playlist(
        self,
        mocked_db,
        mocked_user_repository,
        mocked_track_repository,
        mocked_get_execute_result,
        db_playlist,
        db_update_playlist
    ):

        mocked_get_execute_result.scalar_one_or_none.return_value = db_playlist

        async def mocked_execute(query):
            if 'SELECT' in str(query):
                return mocked_get_execute_result
            return None
        
        mocked_db.execute.side_effect = mocked_execute
                
        async def mock_refresh(instance):
            instance.name = db_update_playlist.name
            instance.description = db_update_playlist.description
            instance.likes = db_update_playlist.likes
            instance.dislikes = db_update_playlist.dislikes
            instance.loves = db_update_playlist.loves
            instance.plays = db_update_playlist.plays
        
        mocked_db.refresh.side_effect = mock_refresh

        repository = PlaylistRepository(mocked_db,mocked_track_repository,mocked_user_repository)

        playlist = await repository.update(db_playlist.id,db_update_playlist)

        assert mocked_db.execute.await_count == 2
        calls = list(map(lambda call: str(call[0][0]),mocked_db.execute.await_args_list))
        id_query = filter(lambda query: 'SELECT' in query and 'WHERE playlists.id =' in query,calls)
        update_query = filter(lambda query: 'UPDATE' in query and 'WHERE playlists.id =' in query,calls)

        assert len(list(id_query)) == 1
        assert len(list(update_query)) == 1

        mocked_db.commit.assert_awaited_once()
        mocked_db.refresh.assert_awaited_once_with(db_playlist)
        self.assert_playlists_equals(playlist,db_update_playlist)
    
    @pytest.mark.asyncio
    async def test_delete_playlist(
        self,
        mocked_db,
        mocked_user_repository,
        mocked_track_repository,
        mocked_get_execute_result,
        db_playlist
    ):

        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = db_playlist

        repository = PlaylistRepository(mocked_db,mocked_track_repository,mocked_user_repository)
        
        result = await repository.delete(db_playlist.id)
        
        mocked_db.execute.assert_awaited_once()
        mocked_db.delete.assert_awaited_once_with(db_playlist)
        mocked_db.commit.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE playlists.id =' in query
        assert result == True
    
    @pytest.mark.parametrize('reaction_type,method_name',[
        ('like','add_like_from_user_to_playlist'),
        ('dislike','add_dislike_from_user_to_playlist'),
        ('love','add_love_from_user_to_playlist')
    ])
    async def test_add_reaction_from_user_to_playlist(
        self,
        reaction_type,
        method_name,
        mocked_db,
        mocked_user_repository,
        mocked_track_repository,
        db_mocked_playlist,
        mocked_get_execute_result,
        db_user
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = db_mocked_playlist

        mocked_user_repository.get_by_id.return_value = db_user

        repository = PlaylistRepository(mocked_db,mocked_track_repository,mocked_user_repository)

        method = getattr(repository,method_name)

        result = await method(db_user.id,db_mocked_playlist.id)

        mocked_db.execute.assert_awaited_once()
        raw_query = mocked_db.execute.await_args[0][0]
        query = str(raw_query)
        assert 'SELECT' in query
        assert 'WHERE playlists.id =' in query
        self.assert_has_selectinload_option(raw_query)

        match reaction_type:

            case 'like':
                db_mocked_playlist.users_likes.append.assert_called_once_with(db_user)
            
            case 'dislike':
                db_mocked_playlist.users_dislikes.append.assert_called_once_with(db_user)
            
            case 'love':
                db_mocked_playlist.users_loves.append.assert_called_once_with(db_user)
        
        mocked_db.commit.assert_awaited_once()
        mocked_db.refresh.assert_awaited_once_with(db_mocked_playlist)

        assert result == True

    @pytest.mark.parametrize('reaction_type,method_name',[
        ('like','remove_like_from_user_to_playlist'),
        ('dislike','remove_dislike_from_user_to_playlist'),
        ('love','remove_love_from_user_to_playlist')
    ])
    async def test_remove_reaction_from_user_to_playlist(
        self,
        reaction_type,
        method_name,
        mocked_db,
        mocked_user_repository,
        mocked_track_repository,
        db_mocked_playlist,
        mocked_get_execute_result,
        db_user
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = db_mocked_playlist

        mocked_user_repository.get_by_id.return_value = db_user

        repository = PlaylistRepository(mocked_db,mocked_track_repository,mocked_user_repository)

        method = getattr(repository,method_name)

        result = await method(db_user.id,db_mocked_playlist.id)

        mocked_db.execute.assert_awaited_once()
        raw_query = mocked_db.execute.await_args[0][0]
        query = str(raw_query)
        assert 'SELECT' in query
        assert 'WHERE playlists.id =' in query
        self.assert_has_selectinload_option(raw_query)

        match reaction_type:

            case 'like':
                db_mocked_playlist.users_likes.remove.assert_called_once_with(db_user)
            
            case 'dislike':
                db_mocked_playlist.users_dislikes.remove.assert_called_once_with(db_user)
            
            case 'love':
                db_mocked_playlist.users_loves.remove.assert_called_once_with(db_user)
        
        mocked_db.commit.assert_awaited_once()
        mocked_db.refresh.assert_awaited_once_with(db_mocked_playlist)

        assert result == True

    @pytest.mark.asyncio
    async def test_add_track_to_playlist(
        self,
        mocked_db,
        mocked_user_repository,
        mocked_track_repository,
        mocked_get_execute_result,
        db_track,
        db_mocked_playlist
    ):

        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = db_mocked_playlist

        mocked_track_repository.get_by_id.return_value = db_track

        repository = PlaylistRepository(mocked_db,mocked_track_repository,mocked_user_repository)

        result = await repository.add_track_to_playlist(db_mocked_playlist.id,db_track.id)

        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE playlists.id =' in query
        db_mocked_playlist.tracks.append.assert_called_once_with(db_track)
        mocked_db.commit.assert_awaited_once()
        mocked_db.refresh.assert_awaited_once_with(db_mocked_playlist)
        assert result == True
    
    @pytest.mark.asyncio
    async def test_remove_track_from_playlist(
        self,
        mocked_db,
        mocked_user_repository,
        mocked_track_repository,
        mocked_get_execute_result,
        db_track,
        db_mocked_playlist
    ):

        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = db_mocked_playlist

        mocked_track_repository.get_by_id.return_value = db_track

        repository = PlaylistRepository(mocked_db,mocked_track_repository,mocked_user_repository)

        result = await repository.remove_track_from_playlist(db_mocked_playlist.id,db_track.id)

        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE playlists.id =' in query
        db_mocked_playlist.tracks.remove.assert_called_once_with(db_track)
        mocked_db.commit.assert_awaited_once()
        mocked_db.refresh.assert_awaited_once_with(db_mocked_playlist)
        assert result == True