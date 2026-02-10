import pytest
import pytest_asyncio
from unittest.mock import AsyncMock,MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from models import Track,User
from repositories import TrackRepository

class TestTrackRepository:

    def assert_has_selectinload_option(self,query):
        if hasattr(query,'_with_options') and query._with_options:
            selectinload_option = list(filter(
                lambda option: 'load' in str(option).lower(),
                query._with_options
            ))
            assert len(selectinload_option) != 0

    @pytest_asyncio.fixture
    async def db_mocked_track(self,db_track):
        track = MagicMock()
        track.id.return_value = db_track.id
        track.users_likes = MagicMock()
        track.users_dislikes = MagicMock()
        track.users_loves = MagicMock()
        return track

    @pytest_asyncio.fixture
    async def db_track(self):
        return Track(
            id='track_id',
            file_id='file_id',
            content_hash='content_hash',
            name='new track',
            author_name='me',
            size='4 Mb',
            likes=0,
            dislikes=0,
            loves=0,
            plays=0,
            uploaded_by='me'
        )

    @pytest_asyncio.fixture
    async def db_update_track(self,db_track):
        return Track(
            id=db_track.id,
            file_id='file_id',
            content_hash='new content_hash',
            name='new new track',
            author_name='me',
            size='5 Mb',
            likes=1,
            dislikes=1,
            loves=1,
            plays=1,
            uploaded_by='me'
        )

    @pytest_asyncio.fixture
    async def db_user(self):
        return User(
            id='user_id',
            username='username',
            email='user@gmail.com',
            hashed_password='hashed_password'
        )

    def assert_tracks_equals(self,track_result:Track | None,track_base:Track):
        assert track_result is not None
        assert track_result.id == track_base.id
        assert track_result.file_id == track_base.file_id
        assert track_result.content_hash == track_base.content_hash
        assert track_result.name == track_base.name
        assert track_result.author_name == track_base.author_name
        assert track_result.size == track_base.size
        assert track_result.likes == track_base.likes
        assert track_result.dislikes == track_base.dislikes
        assert track_result.plays == track_base.plays
        assert track_result.loves == track_base.loves
        assert track_result.uploaded_by == track_base.uploaded_by

    @pytest.mark.asyncio
    async def test_create_track(
        self,
        mocked_db,
        mocked_get_execute_result,
        db_track,
        mocked_user_repository
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = None

        repository = TrackRepository(mocked_db,mocked_user_repository)

        track = await repository.create(db_track)
        
        assert mocked_db.execute.await_count == 2
        for call in mocked_db.execute.await_args_list:
            query = str(call[0][0])
            assert 'SELECT' in query
        
        calls = list(map(lambda call:str(call[0][0]),mocked_db.execute.await_args_list))
        id_query = filter(lambda call: 'WHERE tracks.id =' in call,calls)
        content_hash_query = filter(lambda call: 'WHERE tracks.content_hash =' in call,calls)
        
        assert len(list(id_query)) == 1
        assert len(list(content_hash_query)) == 1

        mocked_db.add.assert_called_once_with(db_track)
        mocked_db.commit.assert_awaited_once()
        mocked_db.refresh.assert_awaited_once_with(db_track)
        self.assert_tracks_equals(track,db_track)        
    
    @pytest.mark.asyncio
    async def test_get_track_by_id(
        self,
        mocked_db,
        mocked_get_execute_result,
        db_track,
        mocked_user_repository
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = db_track

        repository = TrackRepository(mocked_db,mocked_user_repository)

        track = await repository.get_by_id(db_track.id)
        
        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE tracks.id =' in query
        self.assert_tracks_equals(track,db_track)
    
    @pytest.mark.asyncio
    async def test_get_track_by_wrong_id(
        self,
        mocked_db,
        mocked_get_execute_result,
        mocked_user_repository
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = None

        repository = TrackRepository(mocked_db,mocked_user_repository)

        track = await repository.get_by_id('wrong id')
        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE tracks.id =' in query
        assert track is None
    
    @pytest.mark.asyncio
    async def test_update_track(
        self,
        mocked_db,
        mocked_get_execute_result,
        db_track,
        db_update_track,
        mocked_user_repository,
    ):

        mocked_get_execute_result.scalar_one_or_none.return_value = db_track

        async def mock_execute(query):
            if 'SELECT' in str(query):
                return mocked_get_execute_result
            return None
        
        mocked_db.execute.side_effect = mock_execute
        
        async def mock_refresh(instance):
            instance.file_id = db_update_track.file_id
            instance.content_hash = db_update_track.content_hash
            instance.name = db_update_track.name
            instance.author_name = db_update_track.author_name
            instance.size = db_update_track.size
            instance.likes = db_update_track.likes
            instance.dislikes = db_update_track.dislikes
            instance.loves = db_update_track.loves
            instance.plays = db_update_track.plays
            instance.uploaded_by = db_update_track.uploaded_by

        mocked_db.refresh.side_effect = mock_refresh
        
        repository = TrackRepository(mocked_db,mocked_user_repository)

        track = await repository.update(db_track.id,db_update_track)
        
        assert mocked_db.execute.await_count == 2
        calls = list(map(lambda call: str(call[0][0]),mocked_db.execute.await_args_list))
        id_query = filter(lambda call: 'SELECT' in call,calls)
        update_query = filter(lambda call: 'UPDATE' in call and 'WHERE tracks.id =' in call,calls)
        assert len(list(id_query)) == 1
        assert len(list(update_query)) == 1
        mocked_db.commit.assert_awaited_once()
        mocked_db.refresh.assert_awaited_once_with(db_track)
        self.assert_tracks_equals(track,db_update_track)

    @pytest.mark.asyncio
    async def test_delete_track(
        self,
        mocked_db,
        mocked_get_execute_result,
        db_track,
        mocked_user_repository
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = db_track

        repository = TrackRepository(mocked_db,mocked_user_repository)

        result = await repository.delete(db_track.id)
        
        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE tracks.id =' in query
        mocked_db.delete.assert_awaited_once_with(db_track)
        mocked_db.commit.assert_awaited_once()
        assert result == True
    
    @pytest.mark.asyncio
    async def test_delete_wrong_track(
        self,
        mocked_db,
        mocked_get_execute_result,
        db_track,
        mocked_user_repository
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = None

        repository = TrackRepository(mocked_db,mocked_user_repository)

        result = await repository.delete(db_track.id)
        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE tracks.id =' in query
        assert result == False

    @pytest.mark.parametrize('reaction_type,method_name',[
        ('like','add_like_from_user_to_track'),
        ('dislike','add_dislike_from_user_to_track'),
        ('love','add_love_from_user_to_track')
    ])
    async def test_add_reaction_from_user_to_track(
        self,
        reaction_type,
        method_name,
        mocked_db,
        db_mocked_track,
        mocked_get_execute_result,
        db_user,
        mocked_user_repository
    ):
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = db_mocked_track

        mocked_user_repository.get_by_id.return_value = db_user

        repository = TrackRepository(mocked_db,mocked_user_repository)

        method = getattr(repository,method_name)

        result = await method(db_user.id,db_mocked_track.id)

        mocked_db.execute.awaited_once()
        raw_query = mocked_db.execute.await_args[0][0]
        query = str(raw_query)
        assert 'SELECT' in query
        assert 'WHERE tracks.id =' in query
        self.assert_has_selectinload_option(raw_query)
        
        match reaction_type:
            case 'like':
                db_mocked_track.users_likes.append.assert_called_once()
                
            case 'dislike':
                db_mocked_track.users_dislikes.append.assert_called_once()

            case 'love':
                db_mocked_track.users_loves.append.assert_called_once()

        mocked_db.commit.assert_awaited_once()
        mocked_db.refresh.assert_awaited_once_with(db_mocked_track)

        assert result == True

    @pytest.mark.parametrize('reaction_type,method_name',[
        ('like','remove_like_from_user_to_track'),
        ('dislike','remove_dislike_from_user_to_track'),
        ('love','remove_love_from_user_to_track')
    ])
    async def test_remove_reaction_from_user_to_track(
        self,
        reaction_type,
        method_name,
        mocked_db,
        db_mocked_track,
        mocked_get_execute_result,
        db_user,
        mocked_user_repository
    ):
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = db_mocked_track

        mocked_user_repository.get_by_id.return_value = db_user

        repository = TrackRepository(mocked_db,mocked_user_repository)

        method = getattr(repository,method_name)
        
        result = await method(db_user.id,db_mocked_track.id)

        mocked_db.execute.assert_awaited_once()
        raw_query = mocked_db.execute.await_args[0][0]
        query = str(raw_query)
        assert 'SELECT' in query
        assert 'WHERE tracks.id =' in query
        self.assert_has_selectinload_option(raw_query)

        match reaction_type:
            case 'like':
                db_mocked_track.users_likes.remove.assert_called_once_with(db_user)
                
            case 'dislike':
                db_mocked_track.users_dislikes.remove.assert_called_once_with(db_user)

            case 'love':
                db_mocked_track.users_loves.remove.assert_called_once_with(db_user)

        mocked_db.commit.assert_awaited_once()
        mocked_db.refresh.assert_awaited_once_with(db_mocked_track)

        assert result == True