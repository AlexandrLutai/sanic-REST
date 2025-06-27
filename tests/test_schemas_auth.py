import pytest
from pydantic import ValidationError

from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    UserResponse,
    TokenResponse,
    LoginResponse,
    ErrorResponse
)


class TestLoginRequest:
    """Тесты для схемы LoginRequest"""
    
    def test_login_request_valid(self):
        """Тест валидного запроса авторизации"""
        data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        request = LoginRequest(**data)
        
        assert request.email == "test@example.com"
        assert request.password == "password123"
    
    def test_login_request_invalid_email(self):
        """Тест невалидного email"""
        data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)
    
    def test_login_request_short_password(self):
        """Тест слишком короткого пароля"""
        data = {
            "email": "test@example.com",
            "password": "123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_short" for error in errors)
    
    def test_login_request_missing_fields(self):
        """Тест отсутствующих обязательных полей"""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(email="test@example.com")
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" for error in errors)
    
    def test_login_request_empty_password(self):
        """Тест пустого пароля"""
        data = {
            "email": "test@example.com",
            "password": ""
        }
        
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_short" for error in errors)


class TestRegisterRequest:
    """Тесты для схемы RegisterRequest"""
    
    def test_register_request_valid(self):
        """Тест валидного запроса регистрации"""
        data = {
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "Иван Иванов"
        }
        
        request = RegisterRequest(**data)
        
        assert request.email == "newuser@example.com"
        assert request.password == "password123"
        assert request.full_name == "Иван Иванов"
    
    def test_register_request_short_full_name(self):
        """Тест слишком короткого имени"""
        data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "А"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_short" for error in errors)
    
    def test_register_request_long_full_name(self):
        """Тест слишком длинного имени"""
        data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "А" * 101
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_long" for error in errors)
    
    def test_register_request_unicode_name(self):
        """Тест имени с unicode символами"""
        data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Владимир Петрович Козлов"
        }
        
        request = RegisterRequest(**data)
        assert request.full_name == "Владимир Петрович Козлов"
    
    def test_register_request_missing_full_name(self):
        """Тест отсутствующего имени"""
        data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" for error in errors)


class TestUserResponse:
    """Тесты для схемы UserResponse"""
    
    def test_user_response_valid(self):
        """Тест валидного ответа с данными пользователя"""
        data = {
            "id": 1,
            "email": "user@example.com",
            "full_name": "Иван Иванов"
        }
        
        response = UserResponse(**data)
        
        assert response.id == 1
        assert response.email == "user@example.com"
        assert response.full_name == "Иван Иванов"
    
    def test_user_response_invalid_id(self):
        """Тест невалидного ID"""
        data = {
            "id": "not_a_number",
            "email": "user@example.com",
            "full_name": "Иван Иванов"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "int_parsing" for error in errors)
    
    def test_user_response_missing_fields(self):
        """Тест отсутствующих полей"""
        data = {
            "id": 1,
            "email": "user@example.com"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" for error in errors)


class TestTokenResponse:
    """Тесты для схемы TokenResponse"""
    
    def test_token_response_valid(self):
        """Тест валидного ответа с токеном"""
        data = {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "expires_in": 3600
        }
        
        response = TokenResponse(**data)
        
        assert response.access_token == "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        assert response.token_type == "bearer"  # default value
        assert response.expires_in == 3600
    
    def test_token_response_custom_token_type(self):
        """Тест кастомного типа токена"""
        data = {
            "access_token": "token123",
            "token_type": "custom",
            "expires_in": 7200
        }
        
        response = TokenResponse(**data)
        assert response.token_type == "custom"
    
    def test_token_response_invalid_expires_in(self):
        """Тест невалидного времени истечения"""
        data = {
            "access_token": "token123",
            "expires_in": "not_a_number"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TokenResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "int_parsing" for error in errors)


class TestLoginResponse:
    """Тесты для схемы LoginResponse"""
    
    def test_login_response_valid(self):
        """Тест валидного ответа авторизации"""
        data = {
            "user": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "Иван Иванов"
            },
            "token": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }
        
        response = LoginResponse(**data)
        
        assert response.user.id == 1
        assert response.user.email == "user@example.com"
        assert response.token.access_token == "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    
    def test_login_response_invalid_user(self):
        """Тест невалидных данных пользователя"""
        data = {
            "user": {
                "id": "invalid",
                "email": "user@example.com",
                "full_name": "Иван Иванов"
            },
            "token": {
                "access_token": "token123",
                "expires_in": 3600
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            LoginResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "int_parsing" for error in errors)


class TestErrorResponse:
    """Тесты для схемы ErrorResponse"""
    
    def test_error_response_valid(self):
        """Тест валидного ответа с ошибкой"""
        data = {
            "error": "Неверный email или пароль",
            "details": "Пользователь с указанным email не найден"
        }
        
        response = ErrorResponse(**data)
        
        assert response.error == "Неверный email или пароль"
        assert response.details == "Пользователь с указанным email не найден"
    
    def test_error_response_without_details(self):
        """Тест ответа с ошибкой без деталей"""
        data = {
            "error": "Внутренняя ошибка сервера"
        }
        
        response = ErrorResponse(**data)
        
        assert response.error == "Внутренняя ошибка сервера"
        assert response.details is None
    
    def test_error_response_missing_error(self):
        """Тест отсутствующего поля error"""
        data = {
            "details": "Дополнительная информация"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" for error in errors)


class TestSchemasIntegration:
    """Интеграционные тесты схем"""
    
    def test_schemas_json_serialization(self):
        """Тест сериализации схем в JSON"""
        login_request = LoginRequest(email="test@example.com", password="password123")
        
        json_data = login_request.model_dump_json()
        assert '"email":"test@example.com"' in json_data
        assert '"password":"password123"' in json_data
    
    def test_schemas_dict_conversion(self):
        """Тест конвертации схем в словари"""
        user_response = UserResponse(id=1, email="user@example.com", full_name="Test User")
        
        user_dict = user_response.model_dump()
        
        assert user_dict == {
            "id": 1,
            "email": "user@example.com",
            "full_name": "Test User"
        }
    
    def test_nested_schema_validation(self):
        """Тест валидации вложенных схем"""
        # Тест что LoginResponse корректно валидирует вложенные UserResponse и TokenResponse
        data = {
            "user": {
                "id": 1,
                "email": "invalid-email",  # Невалидный email в UserResponse
                "full_name": "Test User"
            },
            "token": {
                "access_token": "token123",
                "expires_in": 3600
            }
        }
        
        # Должно пройти, так как в UserResponse email это просто строка, а не EmailStr
        response = LoginResponse(**data)
        assert response.user.email == "invalid-email"
