"""Pydantic схемы для аутентификации и авторизации"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Схема запроса для авторизации пользователя/администратора"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=6, description="Пароль пользователя")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }
    }


class RegisterRequest(BaseModel):
    """Схема запроса для регистрации нового пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=6, description="Пароль пользователя")
    full_name: str = Field(..., min_length=2, max_length=100, description="Полное имя пользователя")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "newuser@example.com",
                "password": "password123",
                "full_name": "Иван Иванов"
            }
        }
    }


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя"""
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    email: str = Field(..., description="Email пользователя")
    full_name: str = Field(..., description="Полное имя пользователя")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "Иван Иванов"
            }
        }
    }


class TokenResponse(BaseModel):
    """Схема ответа с JWT токеном"""
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни токена в секундах")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }
    }


class LoginResponse(BaseModel):
    """Схема ответа при успешной авторизации"""
    user: UserResponse = Field(..., description="Данные пользователя")
    token: TokenResponse = Field(..., description="Токен доступа")

    model_config = {
        "json_schema_extra": {
            "example": {
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
        }
    }


class ErrorResponse(BaseModel):
    """Схема ответа с ошибкой"""
    error: str = Field(..., description="Описание ошибки")
    details: Optional[str] = Field(None, description="Дополнительные детали ошибки")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "Неверный email или пароль",
                "details": "Пользователь с указанным email не найден"
            }
        }
    }
