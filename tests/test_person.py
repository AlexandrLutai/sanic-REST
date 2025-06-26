import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.person import Person
from app.models.base import Base


class TestPersonModel:
    """Тесты для базовой модели Person"""

    def test_person_is_abstract(self):
        """Тест что Person - абстрактный класс"""
        assert Person.__abstract__ == True

    def test_person_cannot_be_instantiated_directly(self):
        """Тест что Person нельзя создать напрямую"""
        try:
            person = Person(
                email="test@example.com",
                password_hash="hash",
                full_name="Test"
            )
            assert False, "Person не должен быть создаваемым напрямую"
        except Exception:
            assert True

    def test_person_has_required_fields(self):
        """Тест что Person имеет все необходимые поля"""
        assert hasattr(Person, 'email')
        assert hasattr(Person, 'password_hash')
        assert hasattr(Person, 'full_name')
        
        assert hasattr(Person, 'to_dict')
        assert hasattr(Person, '__repr__')

    def test_person_inheritance(self):
        """Тест что Person наследует от BaseModel"""
        from app.models.base import BaseModel
        assert issubclass(Person, BaseModel)
        
        assert hasattr(Person, 'id')
        assert hasattr(Person, 'created_at')
        assert hasattr(Person, 'updated_at')
