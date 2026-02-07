import pytest
from unittest.mock import AsyncMock,MagicMock,patch
from sqlalchemy.ext.asyncio import AsyncSession

from models import Playlist,User
from repositories import PlaylistRepository,TrackRepository,UserRepository

class TestPlaylistRepository:
    
    mock_db = AsyncMock(spec=AsyncSession)
    mock_playlist = Playlist(
        name='my playlists',
        likes=0,
        dislikes=0,
        loves=0,
        plays=0,
        description='description'
    )
    mock_user = User(
        id='user_id',
        username='username',
        email='user@gmail.com',
        hashed_password='hashed_password'
    )

    @pytest.mark.asyncio
    async def test_create_playlist(self):
        self.mock_db.add = MagicMock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        async def mock_refresh(instance):
            if instance is None:
                instance = self.mock_playlist
            if hasattr(instance,'id') and instance.id is None:
                instance.id = 'playlist_id'
        
        self.mock_db.refresh.side_effect = mock_refresh

        with patch('repositories.playlist.PlaylistRepository._try_get_instance',side_effect=lambda x:None):
            user_repository = UserRepository(self.mock_db)
            track_repository = TrackRepository(self.mock_db,user_repository)
            repository = PlaylistRepository(self.mock_db,track_repository,user_repository)

            playlist = await repository.create(self.mock_playlist)
        
        self.mock_db.add.assert_called_once_with(self.mock_playlist)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(self.mock_playlist)

        assert playlist is not None
        assert playlist.id == self.mock_playlist.id
        assert playlist.name == self.mock_playlist.name
        assert playlist.description == self.mock_playlist.description
        assert playlist.likes == self.mock_playlist.likes
        assert playlist.dislikes == self.mock_playlist.dislikes
        assert playlist.plays == self.mock_playlist.plays
        assert playlist.loves == self.mock_playlist.loves
    
    @pytest.mark.asyncio
    async def test_update_playlist(self):

        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        modified_playlist = Playlist(
            name='new name',
            description='new description',
            likes=1,
            dislikes=1,
            loves=1,
            plays=1
        )

        def mock_instance_to_dict(instance):
            return {
                'name':instance.name,
                'description':instance.description,
                'plays':instance.plays,
                'loves':instance.loves,
                'likes':instance.likes,
                'dislikes':instance.dislikes
            }
        
        async def mock_refresh(instance):
            self.mock_playlist.name = modified_playlist.name
            self.mock_playlist.descriptio = modified_playlist.description
            self.mock_playlist.likes = modified_playlist.likes
            self.mock_playlist.dislikes = modified_playlist.dislikes
            self.mock_playlist.loves = modified_playlist.loves
            self.mock_playlist.plays = modified_playlist.plays
        
        self.mock_db.refresh.side_effect = mock_refresh

        with patch('repositories.playlist.PlaylistRepository.get_by_id',return_value=self.mock_playlist):
            with patch('repositories.playlist.PlaylistRepository._instance_to_dict',return_value=mock_instance_to_dict(modified_playlist)):
                user_repository = UserRepository(self.mock_db)
                track_repository = TrackRepository(self.mock_db,user_repository)
                repository = PlaylistRepository(self.mock_db,track_repository,user_repository)

                playlist = await repository.update(self.mock_playlist.id,modified_playlist)
        
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(self.mock_playlist)
        
        assert playlist is not None
        assert playlist.id == self.mock_playlist.id
        assert playlist.name == self.mock_playlist.name
        assert playlist.description == self.mock_playlist.description
        assert playlist.likes == self.mock_playlist.likes
        assert playlist.dislikes == self.mock_playlist.dislikes
        assert playlist.plays == self.mock_playlist.plays
        assert playlist.loves == self.mock_playlist.loves
    
    @pytest.mark.asyncio
    async def test_delete_playlist(self):

        self.mock_db.commit = AsyncMock()
        self.mock_db.delete = AsyncMock()

        with patch('repositories.playlist.PlaylistRepository.get_by_id',return_value=self.mock_playlist):
            user_repository = UserRepository(self.mock_db)
            track_repository = TrackRepository(self.mock_db,user_repository)
            repository = PlaylistRepository(self.mock_db,track_repository,user_repository)

            result = await repository.delete(self.mock_playlist.id)
        
        self.mock_db.delete.assert_awaited_once_with(self.mock_playlist)
        self.mock_db.commit.assert_awaited_once()

        assert result == True
    
    @pytest.mark.asyncio
    async def test_add_like_from_user_to_playlist(self):

        mock_playlist = MagicMock()
        mock_playlist.id = 'playlist_id'
        mock_playlist.users_likes = MagicMock()
        mock_playlist.users_likes.append = MagicMock()

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = mock_playlist
        execute = AsyncMock()
        execute.return_value = mock_execute_result
        self.mock_db.execute = execute
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        with patch('repositories.user.UserRepository.get_by_id',return_value=self.mock_user):
            user_repository = UserRepository(self.mock_db)
            track_repository = TrackRepository(self.mock_db,user_repository)
            repository = PlaylistRepository(self.mock_db,track_repository,user_repository)

            result = await repository.add_like_from_user_to_playlist(self.mock_user.id,self.mock_playlist.id)
        
        execute.assert_awaited_once()
        mock_execute_result.scalar_one_or_none.assert_called_once()
        mock_playlist.users_likes.append.assert_called_once_with(self.mock_user)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(mock_playlist)

        assert result == True
    
    @pytest.mark.asyncio
    async def test_remove_like_from_user_to_playlist(self):

        mock_playlist = MagicMock()
        mock_playlist.id = 'playlist_id'
        mock_playlist.users_likes = MagicMock()
        mock_playlist.users_likes.remove = MagicMock()

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = mock_playlist
        execute = AsyncMock()
        execute.return_value = mock_execute_result
        self.mock_db.execute = execute
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        with patch('repositories.user.UserRepository.get_by_id',return_value=self.mock_user):
            user_repository = UserRepository(self.mock_db)
            track_repository = TrackRepository(self.mock_db,user_repository)
            repository = PlaylistRepository(self.mock_db,track_repository,user_repository)

            result = await repository.remove_like_from_user_to_playlist(self.mock_user.id,self.mock_playlist.id)
        
        execute.assert_awaited_once()
        mock_execute_result.scalar_one_or_none.assert_called_once()
        mock_playlist.users_likes.remove.assert_called_once_with(self.mock_user)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(mock_playlist)

        assert result == True
    
    @pytest.mark.asyncio
    async def test_add_dislike_from_user_to_playlist(self):

        mock_playlist = MagicMock()
        mock_playlist.id = 'playlist_id'
        mock_playlist.users_dislikes = MagicMock()
        mock_playlist.users_dislikes.append = MagicMock()

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = mock_playlist
        execute = AsyncMock()
        execute.return_value = mock_execute_result
        self.mock_db.execute = execute
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        with patch('repositories.user.UserRepository.get_by_id',return_value=self.mock_user):
            user_repository = UserRepository(self.mock_db)
            track_repository = TrackRepository(self.mock_db,user_repository)
            repository = PlaylistRepository(self.mock_db,track_repository,user_repository)

            result = await repository.add_dislike_from_user_to_playlist(self.mock_user.id,self.mock_playlist.id)
        
        execute.assert_awaited_once()
        mock_execute_result.scalar_one_or_none.assert_called_once()
        mock_playlist.users_dislikes.append.assert_called_once_with(self.mock_user)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(mock_playlist)

        assert result == True
    
    @pytest.mark.asyncio
    async def test_remove_dislike_from_user_to_playlist(self):

        mock_playlist = MagicMock()
        mock_playlist.id = 'playlist_id'
        mock_playlist.users_dislikes = MagicMock()
        mock_playlist.users_dislikes.remove = MagicMock()

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = mock_playlist
        execute = AsyncMock()
        execute.return_value = mock_execute_result
        self.mock_db.execute = execute
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        with patch('repositories.user.UserRepository.get_by_id',return_value=self.mock_user):
            user_repository = UserRepository(self.mock_db)
            track_repository = TrackRepository(self.mock_db,user_repository)
            repository = PlaylistRepository(self.mock_db,track_repository,user_repository)

            result = await repository.remove_dislike_from_user_to_playlist(self.mock_user.id,self.mock_playlist.id)
        
        execute.assert_awaited_once()
        mock_execute_result.scalar_one_or_none.assert_called_once()
        mock_playlist.users_dislikes.remove.assert_called_once_with(self.mock_user)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(mock_playlist)

        assert result == True
    
    @pytest.mark.asyncio
    async def test_add_love_from_user_to_playlist(self):

        mock_playlist = MagicMock()
        mock_playlist.id = 'playlist_id'
        mock_playlist.users_loves = MagicMock()
        mock_playlist.users_loves.append = MagicMock()

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = mock_playlist
        execute = AsyncMock()
        execute.return_value = mock_execute_result
        self.mock_db.execute = execute
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        with patch('repositories.user.UserRepository.get_by_id',return_value=self.mock_user):
            user_repository = UserRepository(self.mock_db)
            track_repository = TrackRepository(self.mock_db,user_repository)
            repository = PlaylistRepository(self.mock_db,track_repository,user_repository)

            result = await repository.add_love_from_user_to_playlist(self.mock_user.id,self.mock_playlist.id)
        
        execute.assert_awaited_once()
        mock_execute_result.scalar_one_or_none.assert_called_once()
        mock_playlist.users_loves.append.assert_called_once_with(self.mock_user)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(mock_playlist)

        assert result == True
    
    @pytest.mark.asyncio
    async def test_remove_love_from_user_to_playlist(self):

        mock_playlist = MagicMock()
        mock_playlist.id = 'playlist_id'
        mock_playlist.users_loves = MagicMock()
        mock_playlist.users_loves.remove = MagicMock()

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = mock_playlist
        execute = AsyncMock()
        execute.return_value = mock_execute_result
        self.mock_db.execute = execute
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        with patch('repositories.user.UserRepository.get_by_id',return_value=self.mock_user):
            user_repository = UserRepository(self.mock_db)
            track_repository = TrackRepository(self.mock_db,user_repository)
            repository = PlaylistRepository(self.mock_db,track_repository,user_repository)

            result = await repository.remove_love_from_user_to_playlist(self.mock_user.id,self.mock_playlist.id)
        
        execute.assert_awaited_once()
        mock_execute_result.scalar_one_or_none.assert_called_once()
        mock_playlist.users_loves.remove.assert_called_once_with(self.mock_user)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(mock_playlist)

        assert result == True
    
    @pytest.mark.asyncio
    async def test_add_track_to_playlist(self):

        mock_track = MagicMock()

        mock_playlist = MagicMock()
        mock_playlist.id = 'playlist_id'
        mock_playlist.tracks = MagicMock()
        mock_playlist.tracks.append = MagicMock()

        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        with patch('repositories.track.TrackRepository.get_by_id',return_value=mock_track):
            with patch('repositories.playlist.PlaylistRepository.get_by_id',return_value=mock_playlist):
                user_repository = UserRepository(self.mock_db)
                track_repository = TrackRepository(self.mock_db,user_repository)
                repository = PlaylistRepository(self.mock_db,track_repository,user_repository)

                result = await repository.add_track_to_playlist(mock_playlist.id,mock_track.id)
        
        mock_playlist.tracks.append.assert_called_once_with(mock_track)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(mock_playlist)

        assert result == True
    
    @pytest.mark.asyncio
    async def test_remove_track_from_playlist(self):

        mock_track = MagicMock()

        mock_playlist = MagicMock()
        mock_playlist.id = 'playlist_id'
        mock_playlist.tracks = MagicMock()
        mock_playlist.tracks.remove = MagicMock()

        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        with patch('repositories.track.TrackRepository.get_by_id',return_value=mock_track):
            with patch('repositories.playlist.PlaylistRepository.get_by_id',return_value=mock_playlist):
                user_repository = UserRepository(self.mock_db)
                track_repository = TrackRepository(self.mock_db,user_repository)
                repository = PlaylistRepository(self.mock_db,track_repository,user_repository)

                result = await repository.remove_track_from_playlist(mock_playlist.id,mock_track.id)
        
        mock_playlist.tracks.remove.assert_called_once_with(mock_track)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(mock_playlist)