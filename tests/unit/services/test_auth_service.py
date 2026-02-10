import pytest

from services import AuthService
from schemas import UserSchema
from models import User
from settings import ENVIRONMENT

class TestAuthService:


    @pytest.fixture
    def db_user(self,username,password):
        return User(
            id='user_id',
            username=username,
            email='user@gmail.com',
            hashed_password=ENVIRONMENT.CRYPT_CONTEXT.hash(password)
        )
    
    @pytest.fixture
    def auth_user(self,db_user):
        return UserSchema(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email
        )
    
    @pytest.fixture
    def username(self):
        return 'username'

    @pytest.fixture
    def password(self):
        return 'password'
    
    @pytest.mark.asyncio
    async def test_authenticate_user(
        self,
        mocked_user_repository,
        db_user,
        username,
        password
    ):
        mocked_user_repository.get_by_name.return_value = db_user

        service = AuthService(mocked_user_repository)
        authenticated = await service.authenticate_user(username,password)

        mocked_user_repository.get_by_name.assert_awaited_once_with(username)
        assert authenticated == True
    
    @pytest.mark.asyncio
    async def test_authenticate_wrong_user(
        self,
        mocked_user_repository,
    ):
        mocked_user_repository.get_by_name.return_value = None

        service = AuthService(mocked_user_repository)
        authenticated = await service.authenticate_user('wrong username','wrong password')

        mocked_user_repository.get_by_name.assert_awaited_once_with('wrong username')
        assert authenticated == False
    
    @pytest.mark.asyncio
    async def test_access_token(
        self,
        mocked_user_repository,
        username,
        db_user,
        auth_user
    ):
        mocked_user_repository.get_by_name.return_value = db_user

        service = AuthService(mocked_user_repository)

        token = service.create_access_token({'sub':username})

        failed = False
        try:
            user = await service.get_current_user(token)
            mocked_user_repository.get_by_name.assert_awaited_once_with(username)

            assert user.id == auth_user.id
            assert user.username == auth_user.username
            assert user.email == auth_user.email
        except Exception:
            failed = True
        
        assert failed == False