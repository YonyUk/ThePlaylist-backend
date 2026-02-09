import pytest
from unittest.mock import AsyncMock,patch

from models import User
from repositories import UserRepository
from schemas import UserSchema,UserCreateSchema,UserUpdateSchema
from services import UserService

class TestUserService:

    def assert_users_equals(self,user_result:UserSchema | None,user_base:User):
        assert user_result is not None
        assert user_result.id == user_base.id
        assert user_result.username == user_base.username
        assert user_result.email == user_base.email

    @pytest.mark.asyncio
    async def test_create_user(
        self,
        mocked_user_repository,
        mocked_user,
        mocked_user_create
    ):

        mocked_user_repository.create.return_value = mocked_user
        service = UserService(mocked_user_repository)

        user = await service.create(mocked_user_create)

        mocked_user_repository.create.assert_awaited_once()
        self.assert_users_equals(user,mocked_user)
    
    @pytest.mark.asyncio
    async def test_get_user(
        self,
        mocked_user_repository,
        mocked_user
    ):

        mocked_user_repository.get_by_id.return_value = mocked_user
        service = UserService(mocked_user_repository)

        user = await service.get_by_id(mocked_user.id)

        mocked_user_repository.get_by_id.assert_awaited_once_with(mocked_user.id)
        self.assert_users_equals(user,mocked_user)
    
    @pytest.mark.asyncio
    async def test_get_wrong_user(
        self,
        mocked_user_repository,
        mocked_user
    ):

        mocked_user_repository.get_by_id.return_value = None
        service = UserService(mocked_user_repository)

        user = await service.get_by_id(mocked_user.id)

        mocked_user_repository.get_by_id.assert_awaited_once_with(mocked_user.id)

        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_users(
        self,
        mocked_user_repository,
        mocked_user
    ):

        mocked_user_repository.get_instances.return_value = [mocked_user]
        service = UserService(mocked_user_repository)

        users = await service.get()

        mocked_user_repository.get_instances.assert_awaited_once()

        assert len(users) == 1
        self.assert_users_equals(users[0],mocked_user)
    
    @pytest.mark.asyncio
    async def test_update_user(
        self,
        mocked_user_repository,
        mocked_user,
        mocked_user_update,
        mocked_modified_user
    ):

        mocked_user_repository.get_by_id.return_value=mocked_user
        mocked_user_repository.update = AsyncMock()
        mocked_user_repository.update.return_value = mocked_modified_user

        service = UserService(mocked_user_repository)

        user = await service.update(mocked_user.id,mocked_user_update)

        mocked_user_repository.get_by_id.assert_awaited_once_with(mocked_user.id)
        mocked_user_repository.update.assert_awaited_once()

        self.assert_users_equals(user,mocked_modified_user)
    
    @pytest.mark.asyncio
    async def test_delete_user(
        self,
        mocked_user_repository,
        mocked_user
    ):
        
        mocked_user_repository.delete.return_value = True

        service = UserService(mocked_user_repository)

        result = await service.delete(mocked_user.id)

        mocked_user_repository.delete.assert_awaited_once_with(mocked_user.id)
        assert result == True
    
    @pytest.mark.asyncio
    async def test_delete_wrong_user(
        self,
        mocked_user_repository
    ):

        mocked_user_repository.delete.return_value = False

        service = UserService(mocked_user_repository)

        result = await service.delete('fake id')

        mocked_user_repository.delete.assert_awaited_once_with('fake id')

        assert result == False
    
    @pytest.mark.asyncio
    async def test_get_user_by_name(
        self,
        mocked_user_repository,
        mocked_user
    ):

        mocked_user_repository.get_by_name.return_value = mocked_user

        service = UserService(mocked_user_repository)

        user = await service.get_by_name(mocked_user.username)

        mocked_user_repository.get_by_name.assert_awaited_once_with(mocked_user.username)
        self.assert_users_equals(user,mocked_user)
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(
        self,
        mocked_user_repository,
        mocked_user
    ):

        mocked_user_repository.get_by_email.return_value = mocked_user

        service = UserService(mocked_user_repository)

        user = await service.get_by_email(mocked_user.email)

        mocked_user_repository.get_by_email.assert_awaited_once_with(mocked_user.email)
        self.assert_users_equals(user,mocked_user)
    
    @pytest.mark.asyncio
    async def test_get_user_by_wrong_name(
        self,
        mocked_user_repository
    ):

        mocked_user_repository.get_by_name.return_value = None

        service = UserService(mocked_user_repository)

        user = await service.get_by_name('wrong username')

        mocked_user_repository.get_by_name.assert_awaited_once_with('wrong username')

        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_wrong_email(
        self,
        mocked_user_repository
    ):

        mocked_user_repository.get_by_email.return_value = None

        service = UserService(mocked_user_repository)

        user = await service.get_by_email('wrong email')

        mocked_user_repository.get_by_email.assert_awaited_once_with('wrong email')

        assert user is None