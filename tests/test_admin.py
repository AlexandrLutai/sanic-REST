import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.admin import Admin
from app.models.person import Person
from app.models.base import Base


class TestAdminModel:
    """Тесты для модели Admin"""

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

    def test_admin_creation(self):
        """Тест создания объекта Admin"""
        admin = Admin(
            email="admin@example.com",
            password_hash="admin_hash",
            full_name="Admin User"
        )
        
        assert admin.email == "admin@example.com"
        assert admin.password_hash == "admin_hash"
        assert admin.full_name == "Admin User"
        assert isinstance(admin, Person)

    def test_admin_tablename(self):
        """Тест имени таблицы Admin"""
        assert Admin.__tablename__ == "admins"

    def test_admin_inheritance(self):
        """Тест наследования Admin от Person"""
        assert issubclass(Admin, Person)

    def test_admin_repr(self):
        """Тест строкового представления Admin"""
        admin = Admin(
            id=1,
            email="admin@example.com",
            password_hash="hash",
            full_name="Admin User"
        )
        
        expected_repr = "<Admin(id=1, email='admin@example.com', full_name='Admin User')>"
        assert repr(admin) == expected_repr

    def test_admin_to_dict_without_sensitive(self):
        """Тест конвертации Admin в словарь без чувствительных данных"""
        test_time = datetime.now()
        
        admin = Admin(
            id=1,
            email="admin@example.com",
            password_hash="secret_hash",
            full_name="Admin User"
        )
        admin.created_at = test_time
        admin.updated_at = test_time
        
        data = admin.to_dict(include_sensitive=False)
        
        assert data['id'] == "1"
        assert data['email'] == "admin@example.com"
        assert data['full_name'] == "Admin User"
        assert data['created_at'] == test_time.isoformat()
        assert data['updated_at'] == test_time.isoformat()
        assert 'password_hash' not in data

    def test_admin_to_dict_with_sensitive(self):
        """Тест конвертации Admin в словарь с чувствительными данными"""
        admin = Admin(
            id=1,
            email="admin@example.com",
            password_hash="secret_hash",
            full_name="Admin User"
        )
        
        data = admin.to_dict(include_sensitive=True)
        
        assert data['password_hash'] == "secret_hash"
        assert data['email'] == "admin@example.com"

    def test_admin_to_dict_with_none_timestamps(self):
        """Тест конвертации Admin в словарь с пустыми временными метками"""
        admin = Admin(
            email="admin@example.com",
            password_hash="secret_hash",
            full_name="Admin User"
        )
        
        data = admin.to_dict()
        
        assert data['created_at'] is None
        assert data['updated_at'] is None

    async def test_admin_database_operations(self, test_session):
        """Тест операций с Admin в базе данных"""
        admin = Admin(
            email="db_admin@example.com",
            password_hash="db_hash",
            full_name="DB Test Admin"
        )
        
        test_session.add(admin)
        await test_session.commit()
        await test_session.refresh(admin)
        
        assert admin.id is not None
        assert isinstance(admin.id, int)
        assert admin.created_at is not None
        assert admin.updated_at is not None

    async def test_admin_unique_email(self, test_session):
        """Тест уникальности email для Admin"""
        admin1 = Admin(
            email="unique_admin@example.com",
            password_hash="hash1",
            full_name="Admin 1"
        )
        admin2 = Admin(
            email="unique_admin@example.com",
            password_hash="hash2",
            full_name="Admin 2"
        )
        
        test_session.add(admin1)
        await test_session.commit()
        
        test_session.add(admin2)
        
        with pytest.raises(Exception):
            await test_session.commit()

    async def test_admin_query_by_email(self, test_session):
        """Тест поиска Admin по email"""
        from sqlalchemy import select
        
        admin = Admin(
            email="query_admin@example.com",
            password_hash="query_hash",
            full_name="Query Admin"
        )
        
        test_session.add(admin)
        await test_session.commit()
        
        result = await test_session.execute(
            select(Admin).where(Admin.email == "query_admin@example.com")
        )
        found_admin = result.scalar_one_or_none()
        
        assert found_admin is not None
        assert found_admin.email == "query_admin@example.com"
        assert found_admin.full_name == "Query Admin"

    async def test_admin_update(self, test_session):
        """Тест обновления Admin"""
        admin = Admin(
            email="update_admin@example.com",
            password_hash="original_hash",
            full_name="Original Name"
        )
        
        test_session.add(admin)
        await test_session.commit()
        await test_session.refresh(admin)
        
        admin.full_name = "Updated Admin Name"
        await test_session.commit()
        await test_session.refresh(admin)
        
        assert admin.full_name == "Updated Admin Name"

    async def test_multiple_admins(self, test_session):
        """Тест создания нескольких администраторов"""
        admins = [
            Admin(email="admin1@example.com", password_hash="hash1", full_name="Admin 1"),
            Admin(email="admin2@example.com", password_hash="hash2", full_name="Admin 2"),
        ]
        
        test_session.add_all(admins)
        await test_session.commit()
        
        from sqlalchemy import select
        result = await test_session.execute(select(Admin))
        all_admins = result.scalars().all()
        
        assert len(all_admins) == 2
        emails = [admin.email for admin in all_admins]
        assert "admin1@example.com" in emails
        assert "admin2@example.com" in emails

    async def test_admin_no_relationships_to_accounts_payments(self, test_session):
        """Тест что Admin не имеет связей с Account и Payment"""
        admin = Admin(
            email="admin@example.com",
            password_hash="hash",
            full_name="Admin User"
        )
        
        assert not hasattr(admin, 'accounts')
        assert not hasattr(admin, 'payments')
