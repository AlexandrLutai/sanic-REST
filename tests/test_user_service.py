"""Тесты для сервиса работы с пользователями"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.user_service import UserService
from app.models.user import User


class TestUserService:
    """Тесты для UserService"""

    @pytest.fixture
    def mock_user(self):
        """Мок объекта пользователя"""
        user = User(
            id=1,
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User"
        )
        return user

    @pytest.fixture
    def mock_users_list(self):
        """Мок списка пользователей"""
        return [
            User(id=1, email="user1@example.com", password_hash="hash1", full_name="User One"),
            User(id=2, email="user2@example.com", password_hash="hash2", full_name="User Two")
        ]

    @patch('app.services.user_service.get_db_session')
    async def test_get_user_by_id_found(self, mock_get_db_session, mock_user):
        """Тест успешного поиска пользователя по ID"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user  # Обычный return_value
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await UserService.get_user_by_id(1)
        
        assert result is not None
        assert result.id == 1
        assert result.email == "test@example.com"
        assert result.full_name == "Test User"

    @patch('app.services.user_service.get_db_session')
    async def test_get_user_by_id_not_found(self, mock_get_db_session):
        """Тест поиска несуществующего пользователя"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # Обычный return_value
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await UserService.get_user_by_id(999)
        assert result is None

    @patch('app.services.user_service.get_db_session')
    async def test_get_user_by_email_found(self, mock_get_db_session, mock_user):
        """Тест поиска пользователя по email"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user  # Обычный return_value
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await UserService.get_user_by_email("test@example.com")
        
        assert result is not None
        assert result.email == "test@example.com"

    @patch('app.services.user_service.get_db_session')
    async def test_get_user_by_email_not_found(self, mock_get_db_session):
        """Тест поиска несуществующего пользователя по email"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # Обычный return_value
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await UserService.get_user_by_email("nonexistent@example.com")
        assert result is None

    @patch('app.services.user_service.get_db_session')
    async def test_get_all_users_success(self, mock_get_db_session, mock_users_list):
        """Тест получения всех пользователей"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_users_list
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await UserService.get_all_users()

        assert len(result) == 2
        assert result[0].email == "user1@example.com"
        assert result[1].email == "user2@example.com"

    @patch('app.services.user_service.get_db_session')
    async def test_get_all_users_empty(self, mock_get_db_session):
        """Тест получения пустого списка пользователей"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await UserService.get_all_users()
        assert result == []

    @patch('app.services.user_service.PasswordManager.hash_password')
    @patch('app.services.user_service.get_db_session')
    async def test_create_user_success(self, mock_get_db_session, mock_hash_password):
        """Тест успешного создания пользователя"""
        from unittest.mock import MagicMock
        
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # Синхронный метод
        mock_session.commit = AsyncMock()  # Асинхронный метод
        mock_session.refresh = AsyncMock()  # Асинхронный метод
        mock_result = MagicMock()  # Обычный мок, не AsyncMock
        
        # Настраиваем мок для возврата None (пользователь не существует)
        mock_result.scalar_one_or_none.return_value = None  
        
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_hash_password.return_value = "hashed_password"
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await UserService.create_user(
            email="new@example.com",
            password="password123",
            full_name="New User"
        )

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch('app.services.user_service.get_db_session')
    async def test_create_user_email_exists(self, mock_get_db_session, mock_user):
        """Тест создания пользователя с существующим email"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user  # Пользователь уже существует
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        with pytest.raises(ValueError, match="Пользователь с таким email уже существует"):
            await UserService.create_user(
                email="test@example.com",
                password="password123",
                full_name="Test User"
            )

    @patch('app.services.user_service.PasswordManager.hash_password')
    @patch('app.services.user_service.get_db_session')
    async def test_update_user_success(self, mock_get_db_session, mock_hash_password, mock_user):
        """Тест успешного обновления пользователя"""
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_user)  # Используем AsyncMock для get
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # Email уникальный (обычный return_value)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_hash_password.return_value = "new_hashed_password"
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await UserService.update_user(
            user_id=1,
            email="newemail@example.com",
            password="newpassword",
            full_name="Updated Name"
        )

        assert mock_user.email == "newemail@example.com"
        assert mock_user.full_name == "Updated Name"
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch('app.services.user_service.get_db_session')
    async def test_update_user_not_found(self, mock_get_db_session):
        """Тест обновления несуществующего пользователя"""
        mock_session = AsyncMock()
        mock_session.get.return_value = None
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await UserService.update_user(
            user_id=999,
            email="test@example.com"
        )

        assert result is None

    @patch('app.services.user_service.get_db_session')
    async def test_update_user_email_conflict(self, mock_get_db_session, mock_user):
        """Тест обновления с конфликтующим email"""
        mock_session = AsyncMock()
        mock_session.get.return_value = mock_user
        
        # Создаем другого пользователя с конфликтующим email
        conflicting_user = User(id=2, email="conflict@example.com", full_name="Other")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = conflicting_user
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        with pytest.raises(ValueError, match="Пользователь с таким email уже существует"):
            await UserService.update_user(
                user_id=1,
                email="conflict@example.com"
            )

    @patch('app.services.user_service.get_db_session')
    async def test_delete_user_success(self, mock_get_db_session, mock_user):
        """Тест успешного удаления пользователя"""
        mock_session = AsyncMock()
        mock_session.get.return_value = mock_user
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await UserService.delete_user(1)

        assert result is True
        mock_session.delete.assert_called_once_with(mock_user)
        mock_session.commit.assert_called_once()

    @patch('app.services.user_service.get_db_session')
    async def test_delete_user_not_found(self, mock_get_db_session):
        """Тест удаления несуществующего пользователя"""
        mock_session = AsyncMock()
        mock_session.get.return_value = None
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await UserService.delete_user(999)

        assert result is False
        mock_session.delete.assert_not_called()

    @patch('app.services.user_service.UserService.get_user_by_id')
    async def test_user_exists_true(self, mock_get_user_by_id, mock_user):
        """Тест проверки существования пользователя - существует"""
        mock_get_user_by_id.return_value = mock_user

        result = await UserService.user_exists(1)

        assert result is True
        mock_get_user_by_id.assert_called_once_with(1)

    @patch('app.services.user_service.UserService.get_user_by_id')
    async def test_user_exists_false(self, mock_get_user_by_id):
        """Тест проверки существования пользователя - не существует"""
        mock_get_user_by_id.return_value = None

        result = await UserService.user_exists(999)

        assert result is False
        mock_get_user_by_id.assert_called_once_with(999)

    @patch('app.services.user_service.PasswordManager.hash_password')
    @patch('app.services.user_service.get_db_session')
    async def test_update_user_partial_update(self, mock_get_db_session, mock_hash_password, mock_user):
        """Тест частичного обновления пользователя"""
        mock_session = AsyncMock()
        mock_session.get.return_value = mock_user
        mock_hash_password.return_value = "new_hashed_password"
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        # Обновляем только пароль
        await UserService.update_user(
            user_id=1,
            password="newpassword"
        )

        # Проверяем что пароль изменился, а email и имя остались прежними
        assert mock_user.password_hash == "new_hashed_password"
        assert mock_user.email == "test@example.com"  # не изменился
        assert mock_user.full_name == "Test User"  # не изменился

    @patch('app.services.user_service.get_db_session')
    async def test_update_user_same_email(self, mock_get_db_session, mock_user):
        """Тест обновления пользователя с тем же email"""
        mock_session = AsyncMock()
        mock_session.get.return_value = mock_user
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        # Обновляем с тем же email
        await UserService.update_user(
            user_id=1,
            email="test@example.com",  # тот же email
            full_name="Updated Name"
        )

        # Email не должен проверяться на уникальность
        assert mock_user.full_name == "Updated Name"
        mock_session.execute.assert_not_called()  # Проверка уникальности не вызывается

    def test_user_service_class_structure(self):
        """Тест структуры класса UserService"""
        # Проверяем что все методы существуют
        assert hasattr(UserService, 'get_user_by_id')
        assert hasattr(UserService, 'get_user_by_email')
        assert hasattr(UserService, 'get_all_users')
        assert hasattr(UserService, 'create_user')
        assert hasattr(UserService, 'update_user')
        assert hasattr(UserService, 'delete_user')
        assert hasattr(UserService, 'user_exists')

        # Проверяем что методы статические
        import inspect
        assert inspect.isfunction(UserService.get_user_by_id)
        assert inspect.isfunction(UserService.get_user_by_email)
        assert inspect.isfunction(UserService.get_all_users)
        assert inspect.isfunction(UserService.create_user)
        assert inspect.isfunction(UserService.update_user)
        assert inspect.isfunction(UserService.delete_user)
        assert inspect.isfunction(UserService.user_exists)
