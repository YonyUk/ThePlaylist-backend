import pytest
from httpx import Response,AsyncClient
from string import ascii_letters
import random
from typing import List

from schemas import (
    UserCreateSchema,
    UserUpdateSchema,
    UserSchema
)
from settings import ENVIRONMENT

class TestUserEndpoints:

    def assert_users_equals(
        self,
        user_result:UserSchema,
        user_base:UserSchema | UserCreateSchema | UserUpdateSchema
    ):
        if isinstance(user_base,UserSchema):
            assert user_result.id == user_base.id
            assert user_result.username == user_base.username
            assert user_result.email == user_base.email
        else:
            assert user_result.username == user_base.username
            assert user_result.email == user_base.email
    
    async def create_user(self,client:AsyncClient,user:UserCreateSchema) -> UserSchema | None:
        response = await client.post('users/register',json=user.model_dump())
        return UserSchema(**response.json()) if response.status_code == 201 else None

    async def populate_users(self,client:AsyncClient,users:List[UserCreateSchema]) -> int:
        return len(list(filter(
            lambda user: user is not None,
            [
                await self.create_user(client,user) for user in users
            ]
        )))

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
    def user_update(self):
        return UserUpdateSchema(
            username='new username',
            email='newemail@gmail.com',
            password='new password'
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
        self.assert_users_equals(user_response,user_create)    
    
    @pytest.mark.asyncio
    async def test_get_user(
        self,
        async_client:AsyncClient,
        user_create:UserCreateSchema
    ):
        user = await self.create_user(async_client,user_create)
        assert user is not None
        response = await async_client.get(f'users/{user.id}')
        assert response.status_code == 200
        user_response:UserSchema = UserSchema(**response.json())
        self.assert_users_equals(user_response,user)
    
    @pytest.mark.asyncio
    async def test_get_users(
        self,
        async_client:AsyncClient,
        users_create:List[UserCreateSchema],
    ):

        users_created = await self.populate_users(async_client,users_create)

        response = await async_client.get('users',params={
            'limit':100,
            'page':0
        })
        assert response.status_code == 200
        users = [UserSchema(**user) for user in response.json()]
        assert len(users) == users_created and users_created == len(users_create)

        for user in users:
            
            def compare(user:UserCreateSchema,result:UserSchema) -> bool:
                return user.username == result.username and user.email == result.email
            
            equals = list(filter(lambda user_:compare(user_,user),users_create)) # type: ignore
            assert len(equals) == 1
    
    @pytest.mark.asyncio
    async def test_user_login(
        self,
        async_client:AsyncClient,
        user_create:UserCreateSchema
    ):
        user_created = await self.create_user(async_client,user_create)
        assert user_created is not None
        response = await async_client.post('users/token',data={
            'username':user_create.username,
            'password':user_create.password
        })
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_update_user(
        self,
        async_client:AsyncClient,
        user_create:UserCreateSchema,
        user_update:UserUpdateSchema
    ):
        response:Response = await async_client.post('users/register',json=user_create.model_dump())
        assert response.status_code == 201
        user_response = UserSchema(**response.json())
        response = await async_client.post('users/token',data={
            'username':user_create.username,
            'password':user_create.password
        })
        assert response.status_code == 201
        response = await async_client.put(f'users/{user_response.id}',json=user_update.model_dump())
        assert response.status_code == 202
        user_response = UserSchema(**response.json())
        self.assert_users_equals(user_response,user_update)
    
    @pytest.mark.asyncio
    async def test_delete_user(
        self,
        async_client:AsyncClient,
        user_create:UserCreateSchema
    ):
        response:Response = await async_client.post('users/register',json=user_create.model_dump())
        assert response.status_code == 201
        user_response = UserSchema(**response.json())
        response = await async_client.post('users/token',data={
            'username':user_create.username,
            'password':user_create.password
        })
        assert response.status_code == 201
        response = await async_client.delete(f'users/{user_response.id}')
        assert response.status_code == 202
    
    # @pytest.mark.asyncio
    # async def test_get_me_info(
    #     self,
    #     async_client:AsyncClient,
    #     user_create:UserCreateSchema
    # ):
    #     response:Response = 