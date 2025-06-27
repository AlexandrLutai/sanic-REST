"""Модуль для работы с базой данных"""

from .connection import (
    db_config,
    engine,
    AsyncSessionLocal,
    get_db_session,
    create_tables,
    drop_tables,
    close_db,
    DatabaseConfig,
    TestDatabaseConfig
)

# Импорты для тестов
from sqlalchemy.ext.asyncio import create_async_engine
from ..models.base import Base

__all__ = [
    "db_config",
    "engine", 
    "AsyncSessionLocal",
    "get_db_session",
    "create_tables",
    "drop_tables",
    "close_db",
    "DatabaseConfig",
    "TestDatabaseConfig",
    "create_async_engine",
    "Base"
]
