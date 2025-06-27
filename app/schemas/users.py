"""Pydantic схемы для пользовательских операций"""

from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field


class AccountResponse(BaseModel):
    """Схема ответа с данными счета"""
    id: int = Field(..., description="Уникальный идентификатор счета")
    balance: Decimal = Field(..., description="Баланс счета")
    created_at: datetime = Field(..., description="Дата создания счета")
    updated_at: Optional[datetime] = Field(None, description="Дата последнего обновления")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "balance": "1250.50",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T15:45:00Z"
            }
        }
    }


class PaymentResponse(BaseModel):
    """Схема ответа с данными платежа"""
    id: int = Field(..., description="Уникальный идентификатор платежа")
    transaction_id: str = Field(..., description="Уникальный идентификатор транзакции")
    amount: Decimal = Field(..., description="Сумма пополнения счета пользователя")
    created_at: datetime = Field(..., description="Дата создания платежа")
    updated_at: Optional[datetime] = Field(None, description="Дата последнего обновления")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
                "amount": "100.00",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:31:00Z"
            }
        }
    }


class UserAccountsResponse(BaseModel):
    """Схема ответа со списком счетов пользователя"""
    accounts: List[AccountResponse] = Field(..., description="Список счетов и балансов")

    model_config = {
        "json_schema_extra": {
            "example": {
                "accounts": [
                    {
                        "id": 1,
                        "balance": "1250.50",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-20T15:45:00Z"
                    },
                    {
                        "id": 2,
                        "balance": "750.25",
                        "created_at": "2024-01-10T09:15:00Z",
                        "updated_at": "2024-01-18T14:20:00Z"
                    }
                ]
            }
        }
    }


class UserPaymentsResponse(BaseModel):
    """Схема ответа со списком платежей пользователя"""
    payments: List[PaymentResponse] = Field(..., description="Список платежей пользователя")

    model_config = {
        "json_schema_extra": {
            "example": {
                "payments": [
                    {
                        "id": 1,
                        "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
                        "amount": "100.00",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:31:00Z"
                    }
                ]
            }
        }
    }
