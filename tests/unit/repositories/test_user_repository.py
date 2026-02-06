import pytest
from unittest.mock import AsyncMock,MagicMock,patch
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from repositories import UserRepository

class TestUserRepository:

    mock_db = AsyncMock(spec=AsyncSession)
    mock_user = User(
        username='user',
        email='user@gmail.com',
        hashed_password='hashed_password'
    )

    @pytest.mark.asyncio
    async def test_create_user(self):
        
        self.mock_db.add = MagicMock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        async def mock_refresh(instance):
            if instance is None:
                instance = self.mock_user
            if hasattr(instance,'id') and instance.id is None: # type: ignore
                instance.id = 'user_id' # type: ignore
        
        self.mock_db.refresh.side_effect = mock_refresh

        with patch('repositories.user.UserRepository._try_get_instance',side_effect=lambda x:None):

            repository = UserRepository(self.mock_db)
            user = await repository.create(self.mock_user)
        
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once_with(user)

        assert user is not None
        assert user.id == self.mock_user.id
        assert user.username == self.mock_user.username
        assert user.email == self.mock_user.email
        assert user.hashed_password == self.mock_user.hashed_password
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self):
        with patch('repositories.user.UserRepository.get_by_id',return_value=self.mock_user):
            repository = UserRepository(self.mock_db)
            user = await repository.get_by_id(self.mock_user.id)
        
        assert user is not None
        assert user.id == self.mock_user.id
        assert user.username == self.mock_user.username
        assert user.email == self.mock_user.email
        assert user.hashed_password == self.mock_user.hashed_password
    
    @pytest.mark.asyncio
    async def test_get_user_by_wrong_id(self):
        with patch('repositories.user.UserRepository.get_by_id',return_value=None):
            repository = UserRepository(self.mock_db)
            user = await repository.get_by_id('')
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_name(self):
        with patch('repositories.user.UserRepository.get_by_name',return_value=self.mock_user):
            repository = UserRepository(self.mock_db)
            user = await repository.get_by_name(self.mock_user.username)
        assert user is not None
        assert user.id == self.mock_user.id
        assert user.username == self.mock_user.username
        assert user.email == self.mock_user.email
        assert user.hashed_password == self.mock_user.hashed_password
    
    @pytest.mark.asyncio
    async def test_get_user_by_wrong_name(self):
        with patch('repositories.user.UserRepository.get_by_name',return_value=None):
            repository = UserRepository(self.mock_db)
            user = await repository.get_by_name('')
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_email(self):
        with patch('repositories.user.UserRepository.get_by_email',return_value=self.mock_user):
            repository = UserRepository(self.mock_db)
            user = await repository.get_by_email(self.mock_user.email)
        assert user is not None
        assert user.id == self.mock_user.id
        assert user.username == self.mock_user.username
        assert user.email == self.mock_user.email
        assert user.hashed_password == self.mock_user.hashed_password

    @pytest.mark.asyncio
    async def test_get_user_by_wrong_email(self):
        with patch('repositories.user.UserRepository.get_by_email',return_value=None):
            repository = UserRepository(self.mock_db)
            user = await repository.get_by_email(self.mock_user.username)
        assert user is None
    
    @pytest.mark.asyncio
    async def test_update_user(self):

        modified_user = User(
            id=self.mock_user.id,
            username='other',
            email='other@gmail.com',
            hashed_password='new password'
        )
        
        def instance_to_dict(instance:User) -> dict:
            return {
                'id':instance.id,
                'username':instance.username,
                'email':instance.email,
                'hashed_password':instance.hashed_password
            }

        async def mock_refresh(instance):
            instance.username = modified_user.username
            instance.email = modified_user.email
            instance.hashed_password = modified_user.hashed_password
    
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        self.mock_db.execute = AsyncMock()

        self.mock_db.refresh.side_effect = mock_refresh

        with patch('repositories.user.UserRepository.get_by_id',return_value=self.mock_user):
            with patch('repositories.user.UserRepository._instance_to_dict',return_value=instance_to_dict(modified_user)):
                repository = UserRepository(self.mock_db)
                user = await repository.update(self.mock_user.id,modified_user)

        self.mock_db.commit.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once()
        self.mock_db.refresh.assert_awaited_once()

        assert user is not None
        assert user.id == self.mock_user.id
        assert user.username == modified_user.username
        assert user.email == modified_user.email
        assert user.hashed_password == modified_user.hashed_password

    @pytest.mark.asyncio
    async def test_get_users(self):
        with patch('repositories.user.UserRepository.get_instances',return_value=[self.mock_user]):
            repository = UserRepository(self.mock_db)
            result = await repository.get_instances()

            assert len(result) == 1
            assert result[0] is not None
            assert result[0].id == self.mock_user.id
            assert result[0].username == self.mock_user.username
            assert result[0].email == self.mock_user.email
            assert result[0].hashed_password == self.mock_user.hashed_password