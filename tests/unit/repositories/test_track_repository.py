import pytest
from unittest.mock import AsyncMock,MagicMock,patch
from sqlalchemy.ext.asyncio import AsyncSession

from models import Track,User
from repositories import TrackRepository,UserRepository

class TestTrackRepository:

    mock_db = AsyncMock(spec=AsyncSession)
    mock_track = Track(
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
    mock_user = User(
        id='user_id',
        username='username',
        email='user@gmail.com',
        hashed_password='hashed_password'
    )

    @pytest.mark.asyncio
    async def test_create_track(self):
        
        self.mock_db.add = MagicMock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        async def mock_refresh(instance):
            if instance is None:
                instance = self.mock_track
            if hasattr(instance,'id') and instance.id is None:
                instance.id = 'track_id'
        
        self.mock_db.refresh.side_effect = mock_refresh

        with patch('repositories.track.TrackRepository._try_get_instance',side_effect=lambda x:None):
            user_repository = UserRepository(self.mock_db)
            repository = TrackRepository(self.mock_db,user_repository)

            track = await repository.create(self.mock_track)
        
        self.mock_db.add.assert_called_once_with(self.mock_track)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(self.mock_track)

        assert track is not None
        assert track.id == self.mock_track.id
        assert track.file_id == self.mock_track.file_id
        assert track.content_hash == self.mock_track.content_hash
        assert track.name == self.mock_track.name
        assert track.author_name == self.mock_track.author_name
        assert track.size == self.mock_track.size
        assert track.likes == self.mock_track.likes
        assert track.dislikes == self.mock_track.dislikes
        assert track.plays == self.mock_track.plays
        assert track.loves == self.mock_track.loves
        assert track.uploaded_by == self.mock_track.uploaded_by
    
    @pytest.mark.asyncio
    async def test_get_track_by_id(self):
        with patch('repositories.track.TrackRepository.get_by_id',return_value=self.mock_track):
            user_repository = UserRepository(self.mock_db)
            repository = TrackRepository(self.mock_db,user_repository)

            track = await repository.get_by_id(self.mock_track.id)
        
        assert track is not None
        assert track.id == self.mock_track.id
        assert track.file_id == self.mock_track.file_id
        assert track.content_hash == self.mock_track.content_hash
        assert track.name == self.mock_track.name
        assert track.author_name == self.mock_track.author_name
        assert track.size == self.mock_track.size
        assert track.likes == self.mock_track.likes
        assert track.dislikes == self.mock_track.dislikes
        assert track.plays == self.mock_track.plays
        assert track.loves == self.mock_track.loves
        assert track.uploaded_by == self.mock_track.uploaded_by
    
    @pytest.mark.asyncio
    async def test_get_track_by_wrong_id(self):
        with patch('repositories.track.TrackRepository.get_by_id',return_value=None):
            user_repository = UserRepository(self.mock_db)
            repository = TrackRepository(self.mock_db,user_repository)

            track = await repository.get_by_id(self.mock_track.id)
        
        assert track is None
    
    @pytest.mark.asyncio
    async def test_update_track(self):

        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        modified_track = Track(
            file_id='file_id',
            content_hash='new content_hash',
            name='new new track',
            author_name='me',
            size='5 Mb',
            likes=1,
            dislikes=1,
            loves=1,
            plays=1,
            uploaded_by='me'
        )

        def mock_instance_to_dict(instance):
            return {
                'id':instance.id,
                'file_id':instance.file_id,
                'content_hash':instance.content_hash,
                'name':instance.name,
                'author_name':instance.author_name,
                'size':instance.size,
                'likes':instance.likes,
                'dislikes':instance.likes,
                'loves':instance.loves,
                'plays':instance.plays,
                'uploaded_by':instance.uploaded_by
            }
        
        async def mock_refresh(instance):
            self.mock_track.file_id = modified_track.file_id
            self.mock_track.content_hash = modified_track.content_hash
            self.mock_track.name = modified_track.name
            self.mock_track.author_name = modified_track.author_name
            self.mock_track.size = modified_track.size
            self.mock_track.likes = modified_track.likes
            self.mock_track.dislikes = modified_track.dislikes
            self.mock_track.loves = modified_track.loves
            self.mock_track.plays = modified_track.plays
            self.mock_track.uploaded_by = modified_track.uploaded_by

        self.mock_db.refresh.side_effect = mock_refresh
        
        with patch('repositories.track.TrackRepository.get_by_id',return_value=self.mock_track):
            with patch('repositories.track.TrackRepository._instance_to_dict',return_value=mock_instance_to_dict(modified_track)):
                user_repository = UserRepository(self.mock_db)
                repository = TrackRepository(self.mock_db,user_repository)

                track = await repository.update(self.mock_track.id,modified_track)
        
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(self.mock_track)

        assert track is not None
        assert track.id == self.mock_track.id
        assert track.file_id == modified_track.file_id
        assert track.content_hash == modified_track.content_hash
        assert track.name == modified_track.name
        assert track.author_name == modified_track.author_name
        assert track.size == modified_track.size
        assert track.likes == modified_track.likes
        assert track.dislikes == modified_track.dislikes
        assert track.plays == modified_track.plays
        assert track.loves == modified_track.loves
        assert track.uploaded_by == modified_track.uploaded_by

    @pytest.mark.asyncio
    async def test_delete_track(self):
        self.mock_db.delete = AsyncMock()
        self.mock_db.commit = AsyncMock()

        with patch('repositories.track.TrackRepository.get_by_id',return_value=self.mock_track):
            user_repository = UserRepository(self.mock_db)
            repository = TrackRepository(self.mock_db,user_repository)

            result = await repository.delete(self.mock_track.id)
        
        self.mock_db.delete.assert_awaited_once_with(self.mock_track)
        self.mock_db.commit.assert_awaited_once()

        assert result == True
    
    @pytest.mark.asyncio
    async def test_delete_wrong_track(self):
        
        with patch('repositories.track.TrackRepository.get_by_id',return_value=None):
            user_repository = UserRepository(self.mock_db)
            repository = TrackRepository(self.mock_db,user_repository)

            result = await repository.delete(self.mock_track.id)
        
        assert result == False

    @pytest.mark.asyncio
    async def test_add_like_from_user_to_track(self):

        mock_track = MagicMock()
        mock_track.id = 'track_id'
        mock_track.users_likes = MagicMock()
        mock_track.users_likes.append = MagicMock()

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = mock_track
        execute = AsyncMock()
        execute.return_value = mock_execute_result
        self.mock_db.execute = execute
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        with patch('repositories.user.UserRepository.get_by_id',return_value=self.mock_user):
            user_repository = UserRepository(self.mock_db)
            repository = TrackRepository(self.mock_db,user_repository)

            result = await repository.add_like_from_user_to_track(self.mock_user.id,mock_track.id)
        
        self.mock_db.execute.assert_awaited_once()
        mock_execute_result.scalar_one_or_none.assert_called_once()
        mock_track.users_likes.append.assert_called_once_with(self.mock_user)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(mock_track)

        assert result == True
    
    @pytest.mark.asyncio
    async def test_remove_like_from_user_to_track(self):
        mock_track = MagicMock()
        mock_track.id = 'track_id'
        mock_track.users_like = MagicMock()
        mock_track.users_like.remove = MagicMock()

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = mock_track
        execute = AsyncMock()
        execute.return_value = mock_execute_result
        self.mock_db.execute = execute
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        with patch('repositories.user.UserRepository.get_by_id',return_value=self.mock_user):
            user_repository = UserRepository(self.mock_db)
            repository = TrackRepository(self.mock_db,user_repository)

            result = await repository.remove_like_from_user_to_track(self.mock_user.id,mock_track.id)
        
        self.mock_db.execute.assert_awaited_once()
        mock_execute_result.scalar_one_or_none.assert_called_once()
        mock_track.users_likes.remove.assert_called_once_with(self.mock_user)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(mock_track)

        assert result == True

    @pytest.mark.asyncio
    async def test_add_dislike_from_user_to_track(self):

        mock_track = MagicMock()
        mock_track.id = 'track_id'
        mock_track.users_dislikes = MagicMock()
        mock_track.users_dislikes.append = MagicMock()

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = mock_track
        execute = AsyncMock()
        execute.return_value = mock_execute_result
        self.mock_db.execute = execute
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        with patch('repositories.user.UserRepository.get_by_id',return_value=self.mock_user):
            user_repository = UserRepository(self.mock_db)
            repository = TrackRepository(self.mock_db,user_repository)

            result = await repository.add_dislike_from_user_to_track(self.mock_user.id,mock_track.id)
        
        self.mock_db.execute.assert_awaited_once()
        mock_execute_result.scalar_one_or_none.assert_called_once()
        mock_track.users_dislikes.append.assert_called_once_with(self.mock_user)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(mock_track)

        assert result == True
    
    @pytest.mark.asyncio
    async def test_remove_dislike_from_user_to_track(self):
        mock_track = MagicMock()
        mock_track.id = 'track_id'
        mock_track.users_dislike = MagicMock()
        mock_track.users_dislike.remove = MagicMock()

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = mock_track
        execute = AsyncMock()
        execute.return_value = mock_execute_result
        self.mock_db.execute = execute
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        with patch('repositories.user.UserRepository.get_by_id',return_value=self.mock_user):
            user_repository = UserRepository(self.mock_db)
            repository = TrackRepository(self.mock_db,user_repository)

            result = await repository.remove_dislike_from_user_to_track(self.mock_user.id,mock_track.id)
        
        self.mock_db.execute.assert_awaited_once()
        mock_execute_result.scalar_one_or_none.assert_called_once()
        mock_track.users_dislikes.remove.assert_called_once_with(self.mock_user)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(mock_track)

        assert result == True
    
    @pytest.mark.asyncio
    async def test_add_love_from_user_to_track(self):

        mock_track = MagicMock()
        mock_track.id = 'track_id'
        mock_track.users_loves = MagicMock()
        mock_track.users_loves.append = MagicMock()

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = mock_track
        execute = AsyncMock()
        execute.return_value = mock_execute_result
        self.mock_db.execute = execute
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        with patch('repositories.user.UserRepository.get_by_id',return_value=self.mock_user):
            user_repository = UserRepository(self.mock_db)
            repository = TrackRepository(self.mock_db,user_repository)

            result = await repository.add_love_from_user_to_track(self.mock_user.id,mock_track.id)
        
        self.mock_db.execute.assert_awaited_once()
        mock_execute_result.scalar_one_or_none.assert_called_once()
        mock_track.users_loves.append.assert_called_once_with(self.mock_user)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(mock_track)

        assert result == True
    
    @pytest.mark.asyncio
    async def test_remove_love_from_user_to_track(self):
        mock_track = MagicMock()
        mock_track.id = 'track_id'
        mock_track.users_loves = MagicMock()
        mock_track.users_loves.remove = MagicMock()

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = mock_track
        execute = AsyncMock()
        execute.return_value = mock_execute_result
        self.mock_db.execute = execute
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        with patch('repositories.user.UserRepository.get_by_id',return_value=self.mock_user):
            user_repository = UserRepository(self.mock_db)
            repository = TrackRepository(self.mock_db,user_repository)

            result = await repository.remove_love_from_user_to_track(self.mock_user.id,mock_track.id)
        
        self.mock_db.execute.assert_awaited_once()
        mock_execute_result.scalar_one_or_none.assert_called_once()
        mock_track.users_loves.remove.assert_called_once_with(self.mock_user)
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(mock_track)

        assert result == True