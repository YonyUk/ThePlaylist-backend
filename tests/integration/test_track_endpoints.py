import os
from pathlib import Path
import pytest
from httpx import AsyncClient

from schemas import (
    UserSchema,
    UserCreateSchema,
    TrackSchema,
    TrackPrivateUpdateSchema,
    ExistencialQuerySchema
)

class TestTrackEndpoints:
    
    async def create_user(self,client:AsyncClient,user:UserCreateSchema) -> UserSchema | None:
        response = await client.post('users/register',json=user.model_dump())
        return UserSchema(**response.json()) if response.status_code == 201 else None
    
    async def log_user(self,client:AsyncClient,user:UserCreateSchema) -> UserSchema | None:
        user_created = await self.create_user(client,user)
        if user_created is not None:
            response = await client.post('users/token',data={
                'username':user_created.username,
                'password':user.password
            })
            if response.status_code == 201:
                return user_created
        return None

    async def create_track(
        self,
        client:AsyncClient,
        track_name:str,
        author_name:str,
        file_path:str
    ) -> TrackSchema | None:
        with open(file_path,'rb') as f:
            response = await client.post('tracks/upload',
                params={
                    'track_name':track_name,
                    'author_name':author_name
                },
                files={
                    'data':(file_path,f)
                }
            )
            if response.status_code == 201:
                return TrackSchema(**response.json())
        return None

    def assert_tracks_equals(
        self,
        track_result:TrackSchema,
        track_base:TrackSchema | TrackPrivateUpdateSchema | None,
        track_base_name:str='',
        track_base_author_name:str='',
        track_base_size:int=0,
        owner_id:str=''
    ):
        if isinstance(track_base,TrackSchema):
            assert track_result.name == track_base.name
            assert track_result.author_name == track_base.author_name
            assert track_result.size == track_base.size
            assert track_result.uploaded_by == track_base.uploaded_by
            assert track_result.likes == track_base.likes
            assert track_result.dislikes == track_base.dislikes
            assert track_result.plays == track_base.plays
            assert track_result.loves == track_base.loves
            assert track_result.playlists == track_base.playlists
        elif isinstance(track_base,TrackPrivateUpdateSchema):
            p = track_result.name.rindex('.')
            name = track_result.name[:p]
            assert name == track_base.name
            assert track_result.author_name == track_base.author_name
        else:
            assert track_result.name == track_base_name
            assert track_result.author_name == track_base_author_name
            assert track_result.size == track_base_size
            assert track_result.uploaded_by == owner_id
            assert track_result.likes == 0
            assert track_result.dislikes == 0
            assert track_result.loves == 0
            assert track_result.plays == 0
            assert len(track_result.playlists) == 0

    @pytest.fixture
    def track_update(self):
        return TrackPrivateUpdateSchema(
            name='new track name',
            author_name='new author name'
        )
        
    @pytest.fixture
    def user(self):
        return UserCreateSchema(
            username='username',
            email='user@gmail.com',
            password='password'
        )

    @pytest.fixture
    def filepath(self):
        return os.path.join(os.getcwd(),os.path.join('tests',os.path.join('tests_assets','Awaken.m4a')))
    
    @pytest.fixture
    def track_name(self):
        return 'Awaken'
    
    @pytest.fixture
    def author_name(self):
        return 'DeathClock'
    
    @pytest.mark.asyncio
    async def test_create_track(
        self,
        async_client:AsyncClient,
        track_name,
        author_name,
        user,
        filepath
    ):
        user_created = await self.log_user(async_client,user)
        assert user_created is not None
        with open(filepath,'rb') as f:
            response = await async_client.post(
                f'tracks/upload',
                params={
                    'track_name':track_name,
                    'author_name':author_name
                },
                files={
                    'data':(filepath,f)
                }
            )
            assert response.status_code == 201
            track = TrackSchema(**response.json())
            self.assert_tracks_equals(
                track,
                None,
                Path(filepath).name,
                author_name,
                os.stat(filepath).st_size,
                user_created.id
            )
    
    @pytest.mark.asyncio
    async def test_get_track(
        self,
        async_client:AsyncClient,
        track_name,
        author_name,
        user,
        filepath
    ):
        user_logged = await self.log_user(async_client,user)
        assert user_logged is not None
        track_created = await self.create_track(async_client,track_name,author_name,filepath)
        assert track_created is not None
        response = await async_client.get(f'tracks/{track_created.id}')
        assert response.status_code == 200
        track = TrackSchema(**response.json())
        self.assert_tracks_equals(track,track_created)
    
    @pytest.mark.asyncio
    async def test_update_track(
        self,
        async_client:AsyncClient,
        user,
        track_name,
        author_name,
        filepath,
        track_update
    ):
        user_registered = await self.log_user(async_client,user)
        assert user_registered is not None
        track_created = await self.create_track(async_client,track_name,author_name,filepath)
        assert track_created is not None
        response = await async_client.put(f'tracks/{track_created.id}',json=track_update.model_dump())
        assert response.status_code == 202
        track = TrackSchema(**response.json())
        self.assert_tracks_equals(track,track_update)
    
    @pytest.mark.asyncio
    async def test_delete_track(
        self,
        async_client:AsyncClient,
        user,
        track_name,
        author_name,
        filepath
    ):
        user_registered = await self.log_user(async_client,user)
        assert user_registered is not None
        track_created = await self.create_track(async_client,track_name,author_name,filepath)
        assert track_created is not None
        response = await async_client.delete(f'tracks/{track_created.id}')
        assert response.status_code == 202
    
    @pytest.mark.parametrize('reaction_type',[
        'likes',
        'dislikes',
        'loves',
        'plays'
    ])
    async def test_reactions_interactions(
        self,
        reaction_type,
        async_client:AsyncClient,
        user,
        track_name,
        author_name,
        filepath
    ):
        user_registered = await self.log_user(async_client,user)
        assert user_registered is not None
        track_created = await self.create_track(async_client,track_name,author_name,filepath)
        assert track_created is not None
        url = f'tracks/{track_created.id}/stats/{reaction_type}'
        
        # add interaction to track
        response = await async_client.put(url)
        assert response.status_code == 202
        track_reaction_updated = TrackSchema(**response.json())
        # check interaction result
        match reaction_type:
            case 'likes':
                assert track_reaction_updated.likes == track_created.likes + 1

            case 'dislikes':
                assert track_reaction_updated.dislikes == track_created.dislikes + 1
            
            case 'loves':
                assert track_reaction_updated.loves == track_created.loves + 1
            
            case 'plays':
                assert track_reaction_updated.plays == track_created.plays + 1
        # check interaction from user
        if reaction_type == 'plays':
            return
        response = await async_client.get(url)
        assert response.status_code == 200
        result = ExistencialQuerySchema(**response.json())
        assert result.result == True
        # check interaction remove
        response = await async_client.delete(url)
        assert response.status_code == 202
        track_reaction_deleted = TrackSchema(**response.json())
        # check interaction result
        match reaction_type:
            case 'likes':
                assert track_reaction_deleted.likes == track_reaction_updated.likes - 1

            case 'dislikes':
                assert track_reaction_deleted.dislikes == track_reaction_updated.dislikes - 1
            
            case 'loves':
                assert track_reaction_deleted.loves == track_reaction_updated.loves - 1