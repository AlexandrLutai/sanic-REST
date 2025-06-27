"""Pydantic схемы для обработки вебхуков"""

from decimal import Decimal
from pydantic import BaseModel, Field


class WebhookRequest(BaseModel):
    """Схема запроса для обработки вебхука от платежной системы"""
    transaction_id: str = Field(..., description="Уникальный идентификатор транзакции")
    account_id: int = Field(..., description="Идентификатор счета пользователя")
    user_id: int = Field(..., description="Идентификатор пользователя")
    amount: Decimal = Field(..., gt=0, description="Сумма пополнения счета")
    signature: str = Field(..., description="SHA256 подпись объекта")

    model_config = {
        "json_schema_extra": {
            "example": {
                "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
                "user_id": 1,
                "account_id": 1,
                "amount": 100,
                "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
            }
        }
    }


class WebhookResponse(BaseModel):
    """Схема ответа при обработке вебхука"""
    success: bool = Field(..., description="Успешность обработки")
    message: str = Field(..., description="Сообщение о результате")
    transaction_id: str = Field(..., description="ID обработанной транзакции")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Платеж успешно обработан",
                "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b"
            }
        }
    }
