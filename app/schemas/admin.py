"""Pydantic схемы для административных операций"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class AdminUserResponse(BaseModel):
    """Схема ответа с данными пользователя для админки"""

    id: int = Field(..., description="Уникальный идентификатор пользователя")
    email: str = Field(..., description="Email пользователя")
    full_name: str = Field(..., description="Полное имя пользователя")
    created_at: datetime = Field(..., description="Дата создания пользователя")
    updated_at: Optional[datetime] = Field(
        None, description="Дата последнего обновления"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "Иван Иванов",
                "created_at": "2024-01-10T08:00:00Z",
                "updated_at": "2024-01-15T12:30:00Z",
            }
        }
    }


class AdminAccountResponse(BaseModel):
    """Схема ответа с данными счета для админки"""

    id: int = Field(..., description="Уникальный идентификатор счета")
    balance: Decimal = Field(..., description="Баланс счета")
    created_at: datetime = Field(..., description="Дата создания счета")
    updated_at: Optional[datetime] = Field(
        None, description="Дата последнего обновления"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "balance": "1250.50",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T15:45:00Z",
            }
        }
    }


class UserManagementRequest(BaseModel):
    """Схема запроса для управления пользователем"""

    action: str = Field(
        ..., description="Действие: 'create', 'update', 'delete'"
    )
    full_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Полное имя пользователя",
    )
    email: Optional[EmailStr] = Field(None, description="Email пользователя")
    password: Optional[str] = Field(
        None, min_length=6, description="Пароль пользователя"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "action": "create",
                "email": "newuser@example.com",
                "full_name": "Новый Пользователь",
                "password": "password123",
            }
        }
    }


class AdminUsersListResponse(BaseModel):
    """Схема ответа со списком пользователей для админки"""

    users: List[AdminUserResponse] = Field(
        ..., description="Список пользователей"
    )
    total: int = Field(..., description="Общее количество пользователей")
    page: int = Field(..., description="Номер текущей страницы")
    per_page: int = Field(..., description="Количество элементов на странице")

    model_config = {
        "json_schema_extra": {
            "example": {
                "users": [
                    {
                        "id": 1,
                        "email": "user@example.com",
                        "full_name": "Иван Иванов",
                        "created_at": "2024-01-10T08:00:00Z",
                        "updated_at": "2024-01-15T12:30:00Z",
                    }
                ],
                "total": 150,
                "page": 1,
                "per_page": 20,
            }
        }
    }


class AdminAccountsListResponse(BaseModel):
    """Схема ответа со списком счетов для админки"""

    accounts: List[AdminAccountResponse] = Field(
        ..., description="Список счетов"
    )
    total: int = Field(..., description="Общее количество счетов")
    page: int = Field(..., description="Номер текущей страницы")
    per_page: int = Field(
        ..., description="Количество элементов на странице"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "accounts": [
                    {
                        "id": 1,
                        "balance": "1250.50",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-20T15:45:00Z",
                    }
                ],
                "total": 75,
                "page": 1,
                "per_page": 20,
            }
        }
    }


class AdminOperationResponse(BaseModel):
    """Схема ответа после выполнения административной операции"""

    success: bool = Field(..., description="Успешность операции")
    message: str = Field(..., description="Сообщение о результате операции")
    details: Optional[str] = Field(None, description="Дополнительные детали")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Пользователь успешно создан",
                "details": "Новый пользователь добавлен в систему",
            }
        }
    }
