import pytest
from unittest.mock import AsyncMock,MagicMock,patch
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from repositories import UserRepository

class TestUserRepository:

    def assert_users_equals(self,user_result:User,user_base:User):
        assert user_result is not None
        assert user_result.id == user_base.id
        assert user_result.username == user_base.username
        assert user_result.email == user_base.email
        assert user_result.hashed_password == user_base.hashed_password

    @pytest.mark.asyncio
    async def test_create_user(
        self,
        mocked_db,
        mocked_get_execute_result,
        db_mocked_user
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = None

        repository = UserRepository(mocked_db)
        user = await repository.create(db_mocked_user)

        assert mocked_db.execute.await_count == 3
        for call in mocked_db.execute.await_args_list:
            query = str(call[0][0])
            print(query)
            assert 'SELECT' in query
        
        calls = list(map(lambda call:str(call[0][0]),mocked_db.execute.await_args_list))
        id_query = filter(lambda query: 'WHERE users.id =' in query,calls)
        email_query = filter(lambda query: 'WHERE users.email =' in query,calls)
        username_query = filter(lambda query: 'WHERE users.username =' in query,calls)
        assert len(list(id_query)) == 1
        assert len(list(email_query)) == 1
        assert len(list(username_query)) == 1
            
        mocked_db.add.assert_called_once_with(db_mocked_user)
        mocked_db.commit.assert_awaited_once()
        mocked_db.refresh.assert_awaited_once_with(db_mocked_user)
        self.assert_users_equals(user,db_mocked_user)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(
        self,
        mocked_db,
        mocked_get_execute_result,
        db_mocked_user
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = db_mocked_user
        
        repository = UserRepository(mocked_db)
        user = await repository.get_by_id(db_mocked_user.id)
        
        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE users.id =' in query
        self.assert_users_equals(user,db_mocked_user)

    @pytest.mark.asyncio
    async def test_get_user_by_wrong_id(
        self,
        mocked_db,
        mocked_get_execute_result
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = None

        repository = UserRepository(mocked_db)
        user = await repository.get_by_id('')
        
        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE users.id =' in query
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_name(
        self,
        mocked_db,
        mocked_get_execute_result,
        db_mocked_user
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = db_mocked_user

        repository = UserRepository(mocked_db)
        user = await repository.get_by_name(db_mocked_user.username)

        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE users.username =' in query
        self.assert_users_equals(user,db_mocked_user)
    
    @pytest.mark.asyncio
    async def test_get_user_by_wrong_name(
        self,
        mocked_db,
        mocked_get_execute_result
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = None

        repository = UserRepository(mocked_db)
        user = await repository.get_by_name('')

        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE users.username =' in query
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_email(
        self,
        mocked_db,
        mocked_get_execute_result,
        db_mocked_user
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = db_mocked_user

        repository = UserRepository(mocked_db)
        user = await repository.get_by_email(db_mocked_user.email)

        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE users.email =' in query
        self.assert_users_equals(user,db_mocked_user)

    @pytest.mark.asyncio
    async def test_get_user_by_wrong_email(
        self,
        mocked_db,
        mocked_get_execute_result
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = None

        repository = UserRepository(mocked_db)
        user = await repository.get_by_email('')
        assert user is None
    
    @pytest.mark.asyncio
    async def test_update_user(
        self,
        mocked_db,
        mocked_get_execute_result,
        db_mocked_user,
        db_mocked_update_user
    ):
        
        mocked_get_execute_result.scalar_one_or_none.return_value = db_mocked_user

        async def mock_execute(query):
            if 'SELECT' in str(query):
                return mocked_get_execute_result
            return None
        
        mocked_db.execute.side_effect = mock_execute

        async def mock_refresh(instance):
            instance.username = db_mocked_update_user.username
            instance.email = db_mocked_update_user.email
            instance.hashed_password = db_mocked_update_user.hashed_password

        mocked_db.refresh.side_effect = mock_refresh
        
        repository = UserRepository(mocked_db)
        user = await repository.update(db_mocked_user.id,db_mocked_update_user)

        assert mocked_db.execute.await_count == 2
        calls = list(map(lambda call:str(call[0][0]),mocked_db.execute.await_args_list))
        select_query = filter(lambda query: 'SELECT' in query,calls)
        update_query = filter(lambda query: 'UPDATE' in query,calls)
        assert len(list(select_query)) == 1
        assert len(list(update_query)) == 1
        mocked_db.commit.assert_awaited_once()
        mocked_db.refresh.assert_awaited_once_with(db_mocked_user)
        self.assert_users_equals(user,db_mocked_update_user)

    @pytest.mark.asyncio
    async def test_delete_user(
        self,
        mocked_db,
        mocked_get_execute_result,
        db_mocked_user
    ):
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = db_mocked_user

        repository = UserRepository(mocked_db)
        result = await repository.delete(db_mocked_user.id)

        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE users.id =' in query
        mocked_db.delete.assert_awaited_once_with(db_mocked_user)
        mocked_db.commit.assert_awaited_once()

        assert result == True

    @pytest.mark.asyncio
    async def test_delete_wrong_user(
        self,
        mocked_db,
        mocked_get_execute_result
    ):
        
        mocked_db.execute.return_value = mocked_get_execute_result
        mocked_get_execute_result.scalar_one_or_none.return_value = None
        
        repository = UserRepository(mocked_db)
        result = await repository.delete('wrong_id')

        mocked_db.execute.assert_awaited_once()
        query = str(mocked_db.execute.await_args[0][0])
        assert 'SELECT' in query
        assert 'WHERE users.id =' in query
        assert result == False