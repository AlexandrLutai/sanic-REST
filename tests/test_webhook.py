"""Тесты для роутов обработки вебхуков"""

import pytest
from decimal import Decimal
import hashlib

from app.schemas.webhook import WebhookRequest, WebhookResponse
from app.services.webhook_service import WebhookService


class TestWebhookSchemas:
    """Тесты для схем вебхуков"""
    
    def test_webhook_request_valid(self):
        """Тест корректного запроса вебхука"""
        data = {
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "user_id": 1,
            "account_id": 1,
            "amount": 100,
            "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
        }
        
        webhook = WebhookRequest(**data)
        
        assert webhook.transaction_id == "5eae174f-7cd0-472c-bd36-35660f00132b"
        assert webhook.user_id == 1
        assert webhook.account_id == 1
        assert webhook.amount == Decimal("100")
        assert webhook.signature == "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
    
    def test_webhook_request_invalid_amount(self):
        """Тест некорректной суммы"""
        data = {
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "user_id": 1,
            "account_id": 1,
            "amount": -100,  # отрицательная сумма
            "signature": "test"
        }
        
        with pytest.raises(ValueError):
            WebhookRequest(**data)
    
    def test_webhook_request_zero_amount(self):
        """Тест нулевой суммы"""
        data = {
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "user_id": 1,
            "account_id": 1,
            "amount": 0,  # нулевая сумма
            "signature": "test"
        }
        
        with pytest.raises(ValueError):
            WebhookRequest(**data)
    
    def test_webhook_response_valid(self):
        """Тест корректного ответа вебхука"""
        data = {
            "success": True,
            "message": "Платеж успешно обработан",
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b"
        }
        
        response = WebhookResponse(**data)
        
        assert response.success is True
        assert response.message == "Платеж успешно обработан"
        assert response.transaction_id == "5eae174f-7cd0-472c-bd36-35660f00132b"


class TestWebhookService:
    """Тесты для сервиса обработки вебхуков"""
    
    def test_verify_signature_valid(self):
        """Тест корректной проверки подписи"""
        data = {
            "account_id": 1,
            "amount": "100",
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "user_id": 1
        }
        secret_key = "gfdmhghif38yrf9ew0jkf32"
        
        # Вычисляем ожидаемую подпись
        signature_string = f"{data['account_id']}{data['amount']}{data['transaction_id']}{data['user_id']}{secret_key}"
        expected_signature = hashlib.sha256(signature_string.encode()).hexdigest()
        
        result = WebhookService.verify_signature(data, secret_key, expected_signature)
        assert result is True
    
    def test_verify_signature_invalid(self):
        """Тест некорректной подписи"""
        data = {
            "account_id": 1,
            "amount": "100",
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "user_id": 1
        }
        secret_key = "gfdmhghif38yrf9ew0jkf32"
        wrong_signature = "wrong_signature"
        
        result = WebhookService.verify_signature(data, secret_key, wrong_signature)
        assert result is False
    
    def test_verify_signature_example_from_readme(self):
        """Тест подписи из примера в ТЗ"""
        data = {
            "account_id": 1,
            "amount": "100",
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "user_id": 1
        }
        secret_key = "gfdmhghif38yrf9ew0jkf32"
        expected_signature = "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
        
        result = WebhookService.verify_signature(data, secret_key, expected_signature)
        assert result is True
    
    def test_verify_signature_wrong_secret(self):
        """Тест с неправильным секретным ключом"""
        data = {
            "account_id": 1,
            "amount": "100",
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "user_id": 1
        }
        correct_secret = "gfdmhghif38yrf9ew0jkf32"
        wrong_secret = "wrong_secret"
        
        # Генерируем подпись с правильным ключом
        signature_string = f"{data['account_id']}{data['amount']}{data['transaction_id']}{data['user_id']}{correct_secret}"
        signature = hashlib.sha256(signature_string.encode()).hexdigest()
        
        # Проверяем с неправильным ключом
        result = WebhookService.verify_signature(data, wrong_secret, signature)
        assert result is False
    
    def test_verify_signature_alphabetical_order(self):
        """Тест что поля идут в алфавитном порядке"""
        data = {
            "account_id": 5,
            "amount": "250.50",
            "transaction_id": "test-tx-id",
            "user_id": 10
        }
        secret_key = "test_secret"
        
        # Формируем строку в алфавитном порядке: account_id, amount, transaction_id, user_id
        signature_string = f"5250.50test-tx-id10{secret_key}"
        expected_signature = hashlib.sha256(signature_string.encode()).hexdigest()
        
        result = WebhookService.verify_signature(data, secret_key, expected_signature)
        assert result is True


class TestWebhookIntegration:
    """Интеграционные тесты для вебхука"""
    
    def test_webhook_data_serialization(self):
        """Тест сериализации данных вебхука"""
        webhook_data = {
            "transaction_id": "test-123",
            "user_id": 1,
            "account_id": 2,
            "amount": "150.75",
            "signature": "test_signature"
        }
        
        webhook = WebhookRequest(**webhook_data)
        serialized = webhook.model_dump()
        
        assert serialized["transaction_id"] == "test-123"
        assert serialized["user_id"] == 1
        assert serialized["account_id"] == 2
        assert serialized["amount"] == Decimal("150.75")
        assert serialized["signature"] == "test_signature"
    
    def test_webhook_response_serialization(self):
        """Тест сериализации ответа вебхука"""
        response_data = {
            "success": False,
            "message": "Ошибка обработки",
            "transaction_id": "failed-tx"
        }
        
        response = WebhookResponse(**response_data)
        serialized = response.model_dump()
        
        assert serialized["success"] is False
        assert serialized["message"] == "Ошибка обработки"
        assert serialized["transaction_id"] == "failed-tx"
