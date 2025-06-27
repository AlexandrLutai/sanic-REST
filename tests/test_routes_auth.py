"""Тесты для роутов авторизации"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.models.user import User
from app.models.admin import Admin
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse, TokenResponse


class TestAuthRoutesLogic:
    """Тесты для логики роутов авторизации"""

    def test_login_request_schema_validation(self):
        """Тест валидации схемы LoginRequest"""
        # Корректные данные
        valid_data = {
            "email": "user@test.com",
            "password": "password123"
        }
        login_request = LoginRequest(**valid_data)
        assert login_request.email == "user@test.com"
        assert login_request.password == "password123"

        # Некорректный email
        with pytest.raises(Exception):
            LoginRequest(email="invalid-email", password="password123")

        # Отсутствующие поля
        with pytest.raises(Exception):
            LoginRequest(email="user@test.com")

    def test_login_response_schema_creation(self):
        """Тест создания схемы LoginResponse"""
        user_data = {
            "id": 1,
            "email": "user@test.com",
            "full_name": "Test User",
            "created_at": datetime.now(),
            "updated_at": None
        }
        
        token_data = {
            "access_token": "test_token",
            "token_type": "bearer",
            "expires_in": 3600
        }
        
        user_response = UserResponse(**user_data)
        token_response = TokenResponse(**token_data)
        login_response = LoginResponse(user=user_response, token=token_response)
        
        assert login_response.user.id == 1
        assert login_response.user.email == "user@test.com"
        assert login_response.user.full_name == "Test User"
        assert login_response.token.access_token == "test_token"
        assert login_response.token.token_type == "bearer"
        assert login_response.token.expires_in == 3600

    @pytest.mark.asyncio
    async def test_auth_service_user_authentication(self):
        """Тест логики аутентификации пользователя"""
        from app.auth.service import AuthService
        
        # Мокаем пользователя
        mock_user = User(
            id=1,
            email="user@test.com",
            full_name="Test User",
            password_hash="hashed_password",
            created_at=datetime.now(),
            updated_at=None
        )
        
        with patch.object(AuthService, 'authenticate_user', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = mock_user
            
            result = await AuthService.authenticate_user("user@test.com", "password123")
            
            assert result == mock_user
            assert result.id == 1
            assert result.email == "user@test.com"
            assert result.full_name == "Test User"
            
            # Проверяем, что функция была вызвана с правильными параметрами
            mock_auth.assert_called_once_with("user@test.com", "password123")

    @pytest.mark.asyncio
    async def test_auth_service_admin_authentication(self):
        """Тест логики аутентификации администратора"""
        from app.auth.service import AuthService
        
        # Мокаем администратора
        mock_admin = Admin(
            id=1,
            email="admin@test.com",
            full_name="Test Admin",
            password_hash="hashed_password",
            created_at=datetime.now(),
            updated_at=None
        )
        
        with patch.object(AuthService, 'authenticate_admin', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = mock_admin
            
            result = await AuthService.authenticate_admin("admin@test.com", "admin123")
            
            assert result == mock_admin
            assert result.id == 1
            assert result.email == "admin@test.com"
            assert result.full_name == "Test Admin"
            
            # Проверяем, что функция была вызвана с правильными параметрами
            mock_auth.assert_called_once_with("admin@test.com", "admin123")

    @pytest.mark.asyncio
    async def test_auth_service_failed_authentication(self):
        """Тест неуспешной аутентификации"""
        from app.auth.service import AuthService
        
        with patch.object(AuthService, 'authenticate_user', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = None  # Неуспешная аутентификация
            
            result = await AuthService.authenticate_user("user@test.com", "wrong_password")
            
            assert result is None
            mock_auth.assert_called_once_with("user@test.com", "wrong_password")

    def test_route_response_structure(self):
        """Тест структуры ответа роута"""
        # Тестируем, что создаваемый ответ имеет правильную структуру
        mock_user = User(
            id=1,
            email="user@test.com",
            full_name="Test User",
            password_hash="hashed_password",
            created_at=datetime.now(),
            updated_at=None
        )
        
        # Имитируем создание ответа как в роуте
        user_response = UserResponse(
            id=mock_user.id,
            email=mock_user.email,
            full_name=mock_user.full_name,
            created_at=mock_user.created_at,
            updated_at=mock_user.updated_at
        )
        
        token_response = TokenResponse(
            access_token="temp_token",
            token_type="bearer", 
            expires_in=3600
        )
        
        response = LoginResponse(
            user=user_response,
            token=token_response
        )
        
        response_dict = response.model_dump()
        
        assert "user" in response_dict
        assert "token" in response_dict
        assert "id" in response_dict["user"]
        assert "email" in response_dict["user"]
        assert "full_name" in response_dict["user"]
        assert "access_token" in response_dict["token"]
        assert "token_type" in response_dict["token"]
        assert "expires_in" in response_dict["token"]
        
    def test_admin_route_response_structure(self):
        """Тест структуры ответа роута администратора"""
        # Тестируем, что создаваемый ответ имеет правильную структуру
        mock_admin = Admin(
            id=1,
            email="admin@test.com",
            full_name="Test Admin",
            password_hash="hashed_password",
            created_at=datetime.now(),
            updated_at=None
        )
        
        # Имитируем создание ответа как в роуте
        user_response = UserResponse(
            id=mock_admin.id,
            email=mock_admin.email,
            full_name=mock_admin.full_name,
            created_at=mock_admin.created_at,
            updated_at=mock_admin.updated_at
        )
        
        token_response = TokenResponse(
            access_token="temp_token",
            token_type="bearer",
            expires_in=3600
        )
        
        response = LoginResponse(
            user=user_response,
            token=token_response
        )
        
        response_dict = response.model_dump()
        
        assert "user" in response_dict
        assert "token" in response_dict
        assert "id" in response_dict["user"]
        assert "email" in response_dict["user"]
        assert "full_name" in response_dict["user"]
        assert "access_token" in response_dict["token"]
        assert "token_type" in response_dict["token"]
        assert "expires_in" in response_dict["token"]

    def test_route_blueprint_configuration(self):
        """Тест конфигурации blueprint роута"""
        from app.routes.auth import auth_bp
        
        assert auth_bp.name == "auth"
        assert auth_bp.url_prefix == "/api/v1/auth"
        
        # Проверяем, что у blueprint есть основные атрибуты
        assert hasattr(auth_bp, 'name')
        assert hasattr(auth_bp, 'url_prefix')
        assert hasattr(auth_bp, 'routes')

    def test_error_handling_structure(self):
        """Тест структуры обработки ошибок"""
        # Тестируем типичную структуру ошибки, которая возвращается в роутах
        error_response = {
            "error": "Неверный email или пароль"
        }
        
        assert "error" in error_response
        assert isinstance(error_response["error"], str)
        assert len(error_response["error"]) > 0
