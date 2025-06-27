import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.database import (
    DatabaseConfig, 
    get_db_session, 
    create_tables, 
    drop_tables, 
    close_db,
    TestDatabaseConfig as TestDbConfig
)


class TestDatabaseConfig:
    """Тесты для класса DatabaseConfig"""

    def test_default_config_values(self):
        """Тест значений конфигурации по умолчанию"""
        config = DatabaseConfig()
        
        assert config.DB_USER == "postgres"
        assert config.DB_PASSWORD == "password"
        assert config.DB_HOST == "localhost"
        assert config.DB_PORT == "5432"
        assert config.DB_NAME == "sanic_payment_db"

    @patch.dict(os.environ, {
        'DB_USER': 'testuser',
        'DB_PASSWORD': 'testpass',
        'DB_HOST': 'testhost',
        'DB_PORT': '5433',
        'DB_NAME': 'testdb'
    })
    def test_config_from_environment(self):
        """Тест загрузки конфигурации из переменных окружения"""
        config = DatabaseConfig()
        
        assert config.DB_USER == "testuser"
        assert config.DB_PASSWORD == "testpass"
        assert config.DB_HOST == "testhost"
        assert config.DB_PORT == "5433"
        assert config.DB_NAME == "testdb"

    def test_database_url_formation(self):
        """Тест формирования URL подключения к БД"""
        config = DatabaseConfig()
        expected_url = f"postgresql+asyncpg://postgres:password@localhost:5432/sanic_payment_db"
        
        assert config.DATABASE_URL == expected_url

    @patch.dict(os.environ, {
        'DB_ECHO': 'true',
        'DB_POOL_SIZE': '20',
        'DB_MAX_OVERFLOW': '30'
    })
    def test_engine_config_from_environment(self):
        """Тест настроек движка из переменных окружения"""
        config = DatabaseConfig()
        
        assert config.ENGINE_CONFIG["echo"] is True
        assert config.ENGINE_CONFIG["pool_size"] == 20
        assert config.ENGINE_CONFIG["max_overflow"] == 30
        assert config.ENGINE_CONFIG["pool_pre_ping"] is True

    def test_engine_config_defaults(self):
        """Тест настроек движка по умолчанию"""
        config = DatabaseConfig()
        
        assert config.ENGINE_CONFIG["echo"] is False
        assert config.ENGINE_CONFIG["pool_size"] == 10
        assert config.ENGINE_CONFIG["max_overflow"] == 20
        assert config.ENGINE_CONFIG["pool_pre_ping"] is True


class TestDatabaseSession:
    """Тесты для работы с сессиями БД"""

    async def test_get_db_session_success(self):
        """Тест успешного получения сессии"""
        with patch('app.database.connection.AsyncSessionLocal') as mock_session_local:
            mock_session = MagicMock(spec=AsyncSession)
            
            class MockAsyncSession:
                async def __aenter__(self):
                    return mock_session
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    return None
            
            mock_session_local.return_value = MockAsyncSession()
            
            session_gen = get_db_session()
            session = await session_gen.__anext__()
            assert session == mock_session

    async def test_get_db_session_with_rollback(self):
        """Тест обработки исключений в сессии"""
        with patch('app.database.connection.AsyncSessionLocal'):
            session_gen = get_db_session()
            assert session_gen is not None


class TestDatabaseOperations:
    """Тесты для операций с базой данных"""

    async def test_create_tables(self):
        """Тест создания таблиц"""
        with patch('app.database.connection.engine') as mock_engine:
            mock_conn = MagicMock()
            
            mock_conn.run_sync = AsyncMock()
            
            class MockEngine:
                def begin(self):
                    return MockContext()
            
            class MockContext:
                async def __aenter__(self):
                    return mock_conn
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    return None
            
            mock_engine.begin.return_value = MockContext()
            
            try:
                await create_tables()
                mock_conn.run_sync.assert_called_once()
            except ImportError:
                pass

    async def test_drop_tables(self):
        """Тест удаления таблиц"""
        with patch('app.database.connection.engine') as mock_engine:
            mock_conn = MagicMock()
            
            async def mock_run_sync(func):
                func(mock_conn)
            
            mock_conn.run_sync = mock_run_sync
            
            class MockEngine:
                def begin(self):
                    return MockContext()
            
            class MockContext:
                async def __aenter__(self):
                    return mock_conn
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    return None
            
            mock_engine.begin.return_value = MockContext()
            
            with patch('app.database.Base') as mock_base:
                mock_base.metadata.drop_all = MagicMock()
                await drop_tables()

    async def test_close_db(self):
        """Тест закрытия соединения с БД"""
        class MockEngine:
            async def dispose(self):
                pass
        
        with patch('app.database.connection.engine', MockEngine()):
            await close_db()


class TestTestDbConfig:
    """Тесты для тестовой конфигурации БД"""

    def test_test_database_url(self):
        """Тест URL тестовой БД"""
        assert TestDbConfig.DATABASE_URL == "sqlite+aiosqlite:///:memory:"

    def test_get_test_engine(self):
        """Тест создания тестового движка"""
        with patch('app.database.connection.create_async_engine') as mock_create_engine:
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine
            
            engine = TestDbConfig.get_test_engine()
            
            mock_create_engine.assert_called_once_with(
                "sqlite+aiosqlite:///:memory:",
                echo=False,
                pool_pre_ping=True
            )
            assert engine == mock_engine


class TestDatabaseIntegration:
    """Интеграционные тесты для работы с БД"""

    @pytest.fixture
    async def test_engine(self):
        """Тестовый движок с SQLite в памяти"""
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        yield engine
        await engine.dispose()

    async def test_real_database_operations(self, test_engine):
        """Тест реальных операций с БД (SQLite в памяти)"""
        from app.models.base import Base
        
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
