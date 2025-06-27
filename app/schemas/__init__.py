"""Pydantic схемы для валидации данных запросов и ответов API"""

from .auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
    TokenResponse
)

__all__ = [
    "LoginRequest",
    "LoginResponse", 
    "RegisterRequest",
    "UserResponse",
    "TokenResponse"
]
