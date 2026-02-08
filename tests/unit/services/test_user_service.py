import pytest
from unittest.mock import AsyncMock,patch

from models import User
from repositories import UserRepository
from schemas import UserSchema,UserCreateSchema,UserUpdateSchema
from services import UserService

class TestUserService:

    mock_repository = AsyncMock(spec=UserRepository)
    mock_user = User(
            id='user_id',
            username='username',
            email='user@gmail.com',
            hashed_password='hashed_password'
        )

    @pytest.mark.asyncio
    async def test_create_user(self):

        mock_user_create = UserCreateSchema(
            username='username',
            email='user@gmail.com',
            password='password'
        )

        mock_repository = AsyncMock(spec=UserRepository)
        mock_repository.create.return_value = self.mock_user
        service = UserService(mock_repository)

        user = await service.create(mock_user_create)

        mock_repository.create.assert_awaited_once()

        assert user is not None
        assert user.id == self.mock_user.id
        assert user.username == mock_user_create.username
        assert user.email == mock_user_create.email
    
    @pytest.mark.asyncio
    async def test_get_user(self):

        mock_repository = AsyncMock(spec=UserRepository)
        mock_repository.get_by_id.return_value = self.mock_user
        service = UserService(mock_repository)

        user = await service.get_by_id(self.mock_user.id)

        mock_repository.get_by_id.assert_awaited_once_with(self.mock_user.id)

        assert user is not None
        assert user.id == self.mock_user.id
        assert user.username == self.mock_user.username
        assert user.email == self.mock_user.email
    
    @pytest.mark.asyncio
    async def test_get_wrong_user(self):

        mock_repository = AsyncMock(spec=UserRepository)
        mock_repository.get_by_id.return_value = None
        service = UserService(mock_repository)

        user = await service.get_by_id(self.mock_user.id)

        mock_repository.get_by_id.assert_awaited_once_with(self.mock_user.id)

        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_users(self):

        mock_repository = AsyncMock(spec=UserRepository)
        mock_repository.get_instances.return_value = [self.mock_user]
        service = UserService(mock_repository)

        users = await service.get()

        mock_repository.get_instances.assert_awaited_once()

        assert len(users) == 1
        assert users[0].id == self.mock_user.id
        assert users[0].username == self.mock_user.username
        assert users[0].email == self.mock_user.email
    
    @pytest.mark.asyncio
    async def test_update_user(self):

        mock_user_update = UserUpdateSchema(
            username='new username',
            email='new@gmail.com',
            password='new password'
        )

        mock_modified_user = User(
            id='user_id',
            username='new username',
            email='new@gmail.com',
            hashed_password='new hashed_password'
        )

        mock_repository = AsyncMock(spec=UserRepository)
        mock_repository.get_by_id.return_value=self.mock_user
        mock_repository.update = AsyncMock()
        mock_repository.update.return_value = mock_modified_user

        with patch('services.user.UserService._get_instance',return_value=mock_modified_user):
            service = UserService(mock_repository)

            user = await service.update(self.mock_user.id,mock_user_update)

        
        mock_repository.get_by_id.assert_awaited_once_with(self.mock_user.id)
        mock_repository.update.assert_awaited_once_with(self.mock_user.id,mock_modified_user)

        assert user is not None
        assert user.id == self.mock_user.id
        assert user.username == mock_user_update.username
        assert user.email == mock_user_update.email
    
    @pytest.mark.asyncio
    async def test_delete_user(self):
        
        mock_repository = AsyncMock(spec=UserRepository)
        mock_repository.delete.return_value = True

        service = UserService(mock_repository)

        result = await service.delete(self.mock_user.id)

        mock_repository.delete.assert_awaited_once_with(self.mock_user.id)

        assert result == True
    
    @pytest.mark.asyncio
    async def test_delete_wrong_user(self):

        mock_repository = AsyncMock(spec=UserRepository)
        mock_repository.delete.return_value = False

        service = UserService(mock_repository)

        result = await service.delete('fake id')

        mock_repository.delete.assert_awaited_once_with('fake id')

        assert result == False
    
    @pytest.mark.asyncio
    async def test_get_user_by_name(self):

        mock_repository = AsyncMock(spec=UserRepository)
        mock_repository.get_by_name.return_value = self.mock_user

        service = UserService(mock_repository)

        user = await service.get_by_name(self.mock_user.username)

        mock_repository.get_by_name.assert_awaited_once_with(self.mock_user.username)

        assert user is not None
        assert user.id == self.mock_user.id
        assert user.username == self.mock_user.username
        assert user.email == self.mock_user.email
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self):

        mock_repository = AsyncMock(spec=UserRepository)
        mock_repository.get_by_email.return_value = self.mock_user

        service = UserService(mock_repository)

        user = await service.get_by_email(self.mock_user.email)

        mock_repository.get_by_email.assert_awaited_once_with(self.mock_user.email)

        assert user is not None
        assert user.id == self.mock_user.id
        assert user.username == self.mock_user.username
        assert user.email == self.mock_user.email
    
    @pytest.mark.asyncio
    async def test_get_user_by_wrong_name(self):

        mock_repository = AsyncMock(spec=UserRepository)
        mock_repository.get_by_name.return_value = None

        service = UserService(mock_repository)

        user = await service.get_by_name('wrong username')

        mock_repository.get_by_name.assert_awaited_once_with('wrong username')

        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_wrong_email(self):

        mock_repository = AsyncMock(spec=UserRepository)
        mock_repository.get_by_email.return_value = None

        service = UserService(mock_repository)

        user = await service.get_by_email('wrong email')

        mock_repository.get_by_email.assert_awaited_once_with('wrong email')

        assert user is None