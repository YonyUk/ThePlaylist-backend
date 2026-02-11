import pytest
from httpx import Response,AsyncClient
from string import ascii_letters
import random
from typing import List

from schemas import UserCreateSchema,UserSchema
from settings import ENVIRONMENT

class TestUserEndpoints:

    @pytest.fixture
    def users_count(self):
        return 10

    @pytest.fixture
    def user_create(self):
        return UserCreateSchema(
            username='username',
            email='user@gmail.com',
            password='password'
        )

    @pytest.fixture
    def users_create(self,users_count:int):
        return [
            UserCreateSchema(
                username=''.join(random.choices(ascii_letters,k=10)),
                email=f'{''.join(random.choices(ascii_letters,k=5))}@gmail.com',
                password=''.join(random.choices(ascii_letters,k=10))
            ) for _ in range(users_count)
        ]

    @pytest.mark.asyncio
    async def test_create_user(
        self,
        async_client:AsyncClient,
        user_create:UserCreateSchema,
    ):
        response:Response = await async_client.post('users/register',json=user_create.model_dump())

        assert response.status_code == 201
        user_response:UserSchema = UserSchema(**response.json())
        assert user_response.username == user_create.username
        assert user_response.email == user_create.email

    
    @pytest.mark.asyncio
    async def test_get_user(
        self,
        async_client:AsyncClient,
        user_create:UserCreateSchema
    ):
        response:Response = await async_client.post('users/register',json=user_create.model_dump())
        assert response.status_code == 201
        user = UserSchema(**response.json())
        response = await async_client.get(f'users/{user.id}')

        assert response.status_code == 200
        user_response:UserSchema = UserSchema(**response.json())
        assert user_response.id == user.id
        assert user_response.username == user.username
        assert user_response.email == user.email
    
    @pytest.mark.asyncio
    async def test_get_users(
        self,
        async_client:AsyncClient,
        users_create:List[UserCreateSchema],
        users_count:int
    ):
        for user in users_create:
            response:Response = await async_client.post('users/register',json=user.model_dump())
            assert response.status_code == 201
        
        response = await async_client.get('users',params={
            'limit':100,
            'page':0
        })
        assert response.status_code == 200
        users = [UserSchema(**user) for user in response.json()]
        assert len(users) == users_count
        for user in users:
            
            def compare(user:UserCreateSchema,result:UserSchema) -> bool:
                return user.username == result.username and user.email == result.email
            
            equals = list(filter(lambda user_:compare(user_,user),users_create)) # type: ignore
            assert len(equals) == 1