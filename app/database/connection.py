import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from ..models.base import Base

load_dotenv()


class DatabaseConfig:
    """Конфигурация базы данных"""
    
    def __init__(self):
        self.DB_USER = os.getenv("DB_USER", "postgres")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_PORT = os.getenv("DB_PORT", "5432")
        self.DB_NAME = os.getenv("DB_NAME", "sanic_payment_db")
        
        self.DATABASE_URL = (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
        
        self.ENGINE_CONFIG = {
            "echo": os.getenv("DB_ECHO", "false").lower() == "true",
            "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
            "pool_pre_ping": True,
        }


db_config = DatabaseConfig()

engine = create_async_engine(
    db_config.DATABASE_URL,
    **db_config.ENGINE_CONFIG
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Получить сессию базы данных.
    Используется в dependency injection для Sanic роутов.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """
    Создать все таблицы в базе данных.
    Используется для инициализации БД.
    """
    async with engine.begin() as conn:
        from ..models import User, Admin, Account, Payment
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """
    Удалить все таблицы из базы данных.
    Используется для очистки БД (обычно в тестах).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_db():
    """
    Закрыть соединение с базой данных.
    Используется при завершении приложения.
    """
    await engine.dispose()


class TestDatabaseConfig:
    """Конфигурация тестовой базы данных (SQLite в памяти)"""
    
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    
    @classmethod
    def get_test_engine(cls):
        """Создать тестовый движок"""
        return create_async_engine(
            cls.DATABASE_URL,
            echo=False,
            pool_pre_ping=True
        )
