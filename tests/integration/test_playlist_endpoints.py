import os
import pytest
from httpx import AsyncClient

from schemas import (
    UserSchema,
    UserCreateSchema,
    TrackSchema,
    PlaylistCreateSchema,
    PlaylistPrivateUpdateSchema,
    PlaylistSchema,
    ExistencialQuerySchema
)

class TestPlaylistEndpoints:

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

    async def create_playlist(self,client:AsyncClient,playlist:PlaylistCreateSchema) -> PlaylistSchema | None:
        response = await client.post('playlists/create',json=playlist.model_dump())
        if response.status_code != 201:
            return None
        return PlaylistSchema(**response.json())

    def assert_playlists_equals(
        self,
        playlist_result:PlaylistSchema,
        playlist_base:PlaylistSchema | PlaylistCreateSchema | PlaylistPrivateUpdateSchema
    ):
        assert playlist_result.name == playlist_base.name
        assert playlist_result.description == playlist_base.description
        if isinstance(playlist_base,PlaylistSchema):
            assert playlist_result.author == playlist_base.author
            assert playlist_result.author_id == playlist_base.author_id
            assert playlist_result.id == playlist_base.id
            assert playlist_result.likes == playlist_base.likes
            assert playlist_result.dislikes == playlist_base.dislikes
            assert playlist_result.loves == playlist_base.loves
            assert playlist_result.plays == playlist_base.plays
            assert playlist_result.tracks == playlist_base.tracks

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
    
    @pytest.fixture
    def playlist_create(self):
        return PlaylistCreateSchema(
            name='my playlist',
            description='my playlist description'
        )

    @pytest.fixture
    def playlist_update(self):
        return PlaylistPrivateUpdateSchema(
            name='new playlist name',
            description='new playlist description'
        )

    @pytest.mark.asyncio
    async def test_create_playlist(
        self,
        async_client:AsyncClient,
        user,
        playlist_create
    ):
        user_registerd = await self.log_user(async_client,user)
        assert user_registerd is not None
        response = await async_client.post('playlists/create',json=playlist_create.model_dump())
        assert response.status_code == 201
        track = PlaylistSchema(**response.json())
        self.assert_playlists_equals(track,playlist_create)
        
    @pytest.mark.asyncio
    async def test_get_playlist(
        self,
        async_client:AsyncClient,
        user,
        playlist_create
    ):
        user_registered = await self.log_user(async_client,user)
        assert user_registered is not None
        playlist_created = await self.create_playlist(async_client,playlist_create)
        assert playlist_created is not None
        response = await async_client.get(f'playlists/{playlist_created.id}')
        assert response.status_code == 200
        playlist = PlaylistSchema(**response.json())
        self.assert_playlists_equals(playlist,playlist_created)
    
    @pytest.mark.asyncio
    async def test_update_playlist(
        self,
        async_client:AsyncClient,
        user,
        playlist_create,
        playlist_update
    ):
        user_registered = await self.log_user(async_client,user)
        assert user_registered is not None
        playlist_created = await self.create_playlist(async_client,playlist_create)
        assert playlist_created is not None
        response = await async_client.put(f'playlists/{playlist_created.id}',json=playlist_update.model_dump())
        assert response.status_code == 202
        playlist = PlaylistSchema(**response.json())
        self.assert_playlists_equals(playlist,playlist_update)
    
    @pytest.mark.asyncio
    async def test_delete_playlist(
        self,
        async_client:AsyncClient,
        user,
        playlist_create
    ):
        user_registered = await self.log_user(async_client,user)
        assert user_registered is not None
        playlist_created = await self.create_playlist(async_client,playlist_create)
        assert playlist_created is not None
        response = await async_client.delete(f'playlists/{playlist_created.id}')
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
        playlist_create
    ):
        user_registered = await self.log_user(async_client,user)
        assert user_registered is not None
        playlist_created = await self.create_playlist(async_client,playlist_create)
        assert playlist_created is not None
        url = f'playlists/{playlist_created.id}/stats/{reaction_type}'
        
        # add interaction to track
        response = await async_client.put(url)
        assert response.status_code == 202
        playlist_reaction_updated = PlaylistSchema(**response.json())
        # check interaction result
        match reaction_type:
            case 'likes':
                assert playlist_reaction_updated.likes == playlist_created.likes + 1

            case 'dislikes':
                assert playlist_reaction_updated.dislikes == playlist_created.dislikes + 1
            
            case 'loves':
                assert playlist_reaction_updated.loves == playlist_created.loves + 1
            
            case 'plays':
                assert playlist_reaction_updated.plays == playlist_created.plays + 1
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
        playlist_reaction_deleted = PlaylistSchema(**response.json())
        # check interaction result
        match reaction_type:
            case 'likes':
                assert playlist_reaction_deleted.likes == playlist_reaction_updated.likes - 1

            case 'dislikes':
                assert playlist_reaction_deleted.dislikes == playlist_reaction_updated.dislikes - 1
            
            case 'loves':
                assert playlist_reaction_deleted.loves == playlist_reaction_updated.loves - 1
    
    @pytest.mark.asyncio
    async def test_add_and_remove_track_to_playlist(
        self,
        async_client:AsyncClient,
        user,
        playlist_create,
        track_name,
        author_name,
        filepath
    ):
        user_registered = await self.log_user(async_client,user)
        assert user_registered is not None
        playlist_created = await self.create_playlist(async_client,playlist_create)
        assert playlist_created is not None
        track_created = await self.create_track(async_client,track_name,author_name,filepath)
        assert track_created is not None
        response = await async_client.put(
            f'playlists/{playlist_created.id}/tracks',
            params={'track_id':track_created.id}
        )
        assert response.status_code == 202
        response = await async_client.delete(
            f'playlists/{playlist_created.id}/tracks',
            params={'track_id':track_created.id}
        )
        assert response.status_code == 202