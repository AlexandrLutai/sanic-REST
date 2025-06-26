import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.user import User
from app.models.person import Person
from app.models.base import Base


class TestUserModel:
    """Тесты для модели User"""

    @pytest.fixture
    async def test_engine(self):
        """Тестовый движок с SQLite в памяти"""
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        yield engine
        await engine.dispose()

    @pytest.fixture
    async def test_session(self, test_engine):
        """Тестовая сессия"""
        AsyncSessionLocal = sessionmaker(
            bind=test_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        async with AsyncSessionLocal() as session:
            yield session

    def test_user_creation(self):
        """Тест создания объекта User"""
        user = User(
            email="user@example.com",
            password_hash="hashed_password",
            full_name="Test User"
        )
        
        assert user.email == "user@example.com"
        assert user.password_hash == "hashed_password"
        assert user.full_name == "Test User"
        assert isinstance(user, Person)

    def test_user_tablename(self):
        """Тест имени таблицы User"""
        assert User.__tablename__ == "users"

    def test_user_inheritance(self):
        """Тест наследования User от Person"""
        assert issubclass(User, Person)

    def test_user_repr(self):
        """Тест строкового представления User"""
        user = User(
            id=1,
            email="test@example.com",
            password_hash="hash",
            full_name="Test User"
        )
        
        expected_repr = "<User(id=1, email='test@example.com', full_name='Test User')>"
        assert repr(user) == expected_repr

    def test_user_to_dict_without_sensitive(self):
        """Тест конвертации User в словарь без чувствительных данных"""
        test_time = datetime.now()
        
        user = User(
            id=1,
            email="test@example.com",
            password_hash="secret_hash",
            full_name="Test User"
        )
        user.created_at = test_time
        user.updated_at = test_time
        
        data = user.to_dict(include_sensitive=False)
        
        assert data['id'] == "1"
        assert data['email'] == "test@example.com"
        assert data['full_name'] == "Test User"
        assert data['created_at'] == test_time.isoformat()
        assert data['updated_at'] == test_time.isoformat()
        assert 'password_hash' not in data

    def test_user_to_dict_with_sensitive(self):
        """Тест конвертации User в словарь с чувствительными данными"""
        user = User(
            id=1,
            email="test@example.com",
            password_hash="secret_hash",
            full_name="Test User"
        )
        
        data = user.to_dict(include_sensitive=True)
        
        assert data['password_hash'] == "secret_hash"
        assert data['email'] == "test@example.com"

    def test_user_to_dict_with_none_timestamps(self):
        """Тест конвертации User в словарь с пустыми временными метками"""
        user = User(
            email="test@example.com",
            password_hash="secret_hash",
            full_name="Test User"
        )
        
        data = user.to_dict()
        
        assert data['created_at'] is None
        assert data['updated_at'] is None

    async def test_user_database_operations(self, test_session):
        """Тест операций с User в базе данных"""
        user = User(
            email="db_user@example.com",
            password_hash="db_hash",
            full_name="DB Test User"
        )
        
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        assert user.id is not None
        assert isinstance(user.id, int)
        assert user.created_at is not None
        assert user.updated_at is not None

    async def test_user_unique_email(self, test_session):
        """Тест уникальности email для User"""
        user1 = User(
            email="unique@example.com",
            password_hash="hash1",
            full_name="User 1"
        )
        user2 = User(
            email="unique@example.com",
            password_hash="hash2",
            full_name="User 2"
        )
        
        test_session.add(user1)
        await test_session.commit()
        
        test_session.add(user2)
        
        with pytest.raises(Exception):
            await test_session.commit()

    async def test_user_query_by_email(self, test_session):
        """Тест поиска User по email"""
        from sqlalchemy import select
        
        user = User(
            email="query_user@example.com",
            password_hash="query_hash",
            full_name="Query User"
        )
        
        test_session.add(user)
        await test_session.commit()
        
        # Поиск по email
        result = await test_session.execute(
            select(User).where(User.email == "query_user@example.com")
        )
        found_user = result.scalar_one_or_none()
        
        assert found_user is not None
        assert found_user.email == "query_user@example.com"
        assert found_user.full_name == "Query User"

    async def test_user_update(self, test_session):
        """Тест обновления User"""
        user = User(
            email="update_user@example.com",
            password_hash="original_hash",
            full_name="Original Name"
        )
        
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        user.full_name = "Updated Name"
        await test_session.commit()
        await test_session.refresh(user)
        
        assert user.full_name == "Updated Name"

    async def test_multiple_users(self, test_session):
        """Тест создания нескольких пользователей"""
        users = [
            User(email="user1@example.com", password_hash="hash1", full_name="User 1"),
            User(email="user2@example.com", password_hash="hash2", full_name="User 2"),
            User(email="user3@example.com", password_hash="hash3", full_name="User 3"),
        ]
        
        test_session.add_all(users)
        await test_session.commit()
        
        from sqlalchemy import select
        result = await test_session.execute(select(User))
        all_users = result.scalars().all()
        
        assert len(all_users) == 3
        emails = [user.email for user in all_users]
        assert "user1@example.com" in emails
        assert "user2@example.com" in emails
        assert "user3@example.com" in emails
