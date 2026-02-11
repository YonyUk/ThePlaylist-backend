import pytest

from models import User
from schemas import UserSchema,UserCreateSchema,UserUpdateSchema
from services import UserService

class TestUserService:

    def assert_users_equals(self,user_result:UserSchema | None,user_base:User):
        assert user_result is not None
        assert user_result.id == user_base.id
        assert user_result.username == user_base.username
        assert user_result.email == user_base.email

    @pytest.fixture
    def db_user(self):
        return UserSchema(
            id='user_id',
            username='username',
            email='user@gmail.com'
        )
    
    @pytest.fixture
    def user_create(self,db_user):
        return UserCreateSchema(
            username=db_user.username,
            email=db_user.email,
            password='my_password'
        )

    @pytest.fixture
    def user_update(self):
        return UserUpdateSchema(
            username='new username',
            email='new@gmail.com',
            password='new password'
        )

    @pytest.fixture
    def updated_user(self,db_user,user_update):
        return UserSchema(
            id=db_user.id,
            email=user_update.email,
            username=user_update.username
        )
    
    @pytest.mark.asyncio
    async def test_create_user(
        self,
        mocked_user_repository,
        user_create,
        db_user
    ):

        mocked_user_repository.create.return_value = db_user
        service = UserService(mocked_user_repository)

        user = await service.create(user_create)

        mocked_user_repository.create.assert_awaited_once()
        self.assert_users_equals(user,db_user)
    
    @pytest.mark.asyncio
    async def test_get_user(
        self,
        mocked_user_repository,
        db_user
    ):

        mocked_user_repository.get_by_id.return_value = db_user
        service = UserService(mocked_user_repository)

        user = await service.get_by_id(db_user.id)

        mocked_user_repository.get_by_id.assert_awaited_once_with(db_user.id)
        self.assert_users_equals(user,db_user)
    
    @pytest.mark.asyncio
    async def test_get_wrong_user(
        self,
        mocked_user_repository
    ):

        mocked_user_repository.get_by_id.return_value = None
        service = UserService(mocked_user_repository)

        user = await service.get_by_id('wrong id')

        mocked_user_repository.get_by_id.assert_awaited_once_with('wrong id')

        assert user is None
    
    @pytest.mark.asyncio
    async def test_update_user(
        self,
        mocked_user_repository,
        db_user,
        user_update,
        updated_user
    ):

        mocked_user_repository.get_by_id.return_value=db_user
        mocked_user_repository.update.return_value = updated_user

        service = UserService(mocked_user_repository)

        user = await service.update(db_user.id,user_update)

        mocked_user_repository.get_by_id.assert_awaited_once_with(db_user.id)
        mocked_user_repository.update.assert_awaited_once()
        self.assert_users_equals(user,updated_user)
    
    @pytest.mark.asyncio
    async def test_delete_user(
        self,
        mocked_user_repository,
        db_user
    ):
        
        mocked_user_repository.delete.return_value = True

        service = UserService(mocked_user_repository)

        result = await service.delete(db_user.id)

        mocked_user_repository.delete.assert_awaited_once_with(db_user.id)
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
        db_user
    ):

        mocked_user_repository.get_by_name.return_value = db_user

        service = UserService(mocked_user_repository)

        user = await service.get_by_name(db_user.username)

        mocked_user_repository.get_by_name.assert_awaited_once_with(db_user.username)
        self.assert_users_equals(user,db_user)
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(
        self,
        mocked_user_repository,
        db_user
    ):

        mocked_user_repository.get_by_email.return_value = db_user

        service = UserService(mocked_user_repository)

        user = await service.get_by_email(db_user.email)

        mocked_user_repository.get_by_email.assert_awaited_once_with(db_user.email)
        self.assert_users_equals(user,db_user)
    
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