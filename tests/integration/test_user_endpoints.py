import pytest
from httpx import Response

from schemas import UserCreateSchema,UserSchema
from settings import ENVIRONMENT

class TestUserEndpoints:

    @pytest.fixture
    def user_create(self):
        return UserCreateSchema(
            username='username',
            email='user@gmail.com',
            password='password'
        )

    @pytest.mark.asyncio
    async def test_create_user(
        self,
        async_client,
        user_create
    ):
        response:Response = await async_client.post('users/register',json=user_create.model_dump())

        assert response.status_code == 201
        user_response:UserSchema = UserSchema(**response.json())
        assert user_response.username == user_create.username
        assert user_response.email == user_create.email