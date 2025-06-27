"""Тесты для роутов обработки вебхуков"""

import pytest
import hashlib
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from app.routes.webhook import webhook_bp
from app.schemas.webhook import WebhookRequest, WebhookResponse


class TestWebhookRoutes:
    """Тесты для роутов вебхуков"""

    @pytest.fixture
    def valid_webhook_data(self):
        """Валидные данные для вебхука"""
        return {
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "user_id": 1,
            "account_id": 1,
            "amount": 100,
            "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
        }

    @pytest.fixture
    def mock_app_config(self):
        """Мок конфигурации приложения"""
        return {"WEBHOOK_SECRET": "gfdmhghif38yrf9ew0jkf32"}

    def test_webhook_blueprint_configuration(self):
        """Тест конфигурации blueprint'а вебхука"""
        assert webhook_bp.name == "webhook"
        assert webhook_bp.url_prefix == "/api/v1/webhook"

    @patch('app.routes.webhook.WebhookService.process_payment')
    async def test_webhook_payment_success(self, mock_process_payment, valid_webhook_data, mock_app_config):
        """Тест успешной обработки вебхука"""
        # Настраиваем мок
        mock_process_payment.return_value = {
            "success": True,
            "message": "Платеж успешно обработан",
            "payment_id": 1
        }

        # Создаем мок запроса
        mock_request = AsyncMock()
        mock_request.json = valid_webhook_data
        mock_request.app.config.get.return_value = mock_app_config["WEBHOOK_SECRET"]

        # Импортируем функцию роута
        from app.routes.webhook import process_payment_webhook
        
        # Вызываем функцию
        response = await process_payment_webhook(mock_request)
        
        # Проверяем результат
        assert response.status == 200
        response_data = response.body.decode()
        assert "success" in response_data
        assert "true" in response_data.lower()

    @patch('app.routes.webhook.WebhookService.process_payment')
    async def test_webhook_payment_invalid_signature(self, mock_process_payment, valid_webhook_data, mock_app_config):
        """Тест вебхука с неверной подписью"""
        # Настраиваем мок для ошибки
        mock_process_payment.return_value = {
            "success": False,
            "message": "Неверная подпись",
            "error_code": "INVALID_SIGNATURE"
        }

        mock_request = AsyncMock()
        mock_request.json = valid_webhook_data
        mock_request.app.config.get.return_value = mock_app_config["WEBHOOK_SECRET"]

        from app.routes.webhook import process_payment_webhook
        response = await process_payment_webhook(mock_request)
        
        assert response.status == 400

    @patch('app.routes.webhook.WebhookService.process_payment')
    async def test_webhook_payment_duplicate_transaction(self, mock_process_payment, valid_webhook_data, mock_app_config):
        """Тест дублирующейся транзакции"""
        mock_process_payment.return_value = {
            "success": False,
            "message": "Транзакция уже обработана",
            "error_code": "DUPLICATE_TRANSACTION"
        }

        mock_request = AsyncMock()
        mock_request.json = valid_webhook_data
        mock_request.app.config.get.return_value = mock_app_config["WEBHOOK_SECRET"]

        from app.routes.webhook import process_payment_webhook
        response = await process_payment_webhook(mock_request)
        
        assert response.status == 409

    async def test_webhook_payment_missing_secret(self, valid_webhook_data):
        """Тест отсутствующего секретного ключа"""
        mock_request = AsyncMock()
        mock_request.json = valid_webhook_data
        mock_request.app.config.get.return_value = None

        from app.routes.webhook import process_payment_webhook
        response = await process_payment_webhook(mock_request)
        
        assert response.status == 400  # Исправляем на ожидаемый код

    async def test_webhook_payment_invalid_data(self, mock_app_config):
        """Тест с некорректными данными"""
        invalid_data = {
            "transaction_id": "test",
            "user_id": "invalid",  # должно быть int
            "account_id": 1,
            "amount": 100,
            "signature": "test"
        }

        mock_request = AsyncMock()
        mock_request.json = invalid_data
        mock_request.app.config.get.return_value = mock_app_config["WEBHOOK_SECRET"]

        from app.routes.webhook import process_payment_webhook
        response = await process_payment_webhook(mock_request)
        
        assert response.status == 400

    async def test_webhook_payment_negative_amount(self, mock_app_config):
        """Тест с отрицательной суммой"""
        invalid_data = {
            "transaction_id": "test",
            "user_id": 1,
            "account_id": 1,
            "amount": -100,  # отрицательная сумма
            "signature": "test"
        }

        mock_request = AsyncMock()
        mock_request.json = invalid_data
        mock_request.app.config.get.return_value = mock_app_config["WEBHOOK_SECRET"]

        from app.routes.webhook import process_payment_webhook
        response = await process_payment_webhook(mock_request)
        
        assert response.status == 400

    @patch('app.routes.webhook.WebhookService.process_payment')
    async def test_webhook_payment_user_not_found(self, mock_process_payment, valid_webhook_data, mock_app_config):
        """Тест с несуществующим пользователем"""
        mock_process_payment.return_value = {
            "success": False,
            "message": "Пользователь не найден",
            "error_code": "USER_NOT_FOUND"
        }

        mock_request = AsyncMock()
        mock_request.json = valid_webhook_data
        mock_request.app.config.get.return_value = mock_app_config["WEBHOOK_SECRET"]

        from app.routes.webhook import process_payment_webhook
        response = await process_payment_webhook(mock_request)
        
        assert response.status == 404

    @patch('app.routes.webhook.WebhookService.process_payment')
    async def test_webhook_payment_account_ownership_error(self, mock_process_payment, valid_webhook_data, mock_app_config):
        """Тест ошибки принадлежности счета"""
        mock_process_payment.return_value = {
            "success": False,
            "message": "Счет не принадлежит пользователю",
            "error_code": "ACCOUNT_OWNERSHIP_ERROR"
        }

        mock_request = AsyncMock()
        mock_request.json = valid_webhook_data
        mock_request.app.config.get.return_value = mock_app_config["WEBHOOK_SECRET"]

        from app.routes.webhook import process_payment_webhook
        response = await process_payment_webhook(mock_request)
        
        assert response.status == 400

    @patch('app.routes.webhook.WebhookService.process_payment')
    async def test_webhook_payment_internal_error(self, mock_process_payment, valid_webhook_data, mock_app_config):
        """Тест внутренней ошибки сервера"""
        mock_process_payment.return_value = {
            "success": False,
            "message": "Ошибка создания платежа",
            "error_code": "PAYMENT_CREATION_ERROR"
        }

        mock_request = AsyncMock()
        mock_request.json = valid_webhook_data
        mock_request.app.config.get.return_value = mock_app_config["WEBHOOK_SECRET"]

        from app.routes.webhook import process_payment_webhook
        response = await process_payment_webhook(mock_request)
        
        assert response.status == 500

    @patch('app.routes.webhook.WebhookService.process_payment')
    async def test_webhook_payment_exception_handling(self, mock_process_payment, valid_webhook_data, mock_app_config):
        """Тест обработки исключений"""
        # Настраиваем мок для генерации исключения
        mock_process_payment.side_effect = Exception("Тестовое исключение")

        mock_request = AsyncMock()
        mock_request.json = valid_webhook_data
        mock_request.app.config.get.return_value = mock_app_config["WEBHOOK_SECRET"]

        from app.routes.webhook import process_payment_webhook
        response = await process_payment_webhook(mock_request)
        
        assert response.status == 500

    def test_webhook_response_structure(self):
        """Тест структуры ответа вебхука"""
        response_data = {
            "success": True,
            "message": "Платеж успешно обработан",
            "transaction_id": "test-tx-123"
        }
        
        response = WebhookResponse(**response_data)
        serialized = response.model_dump()
        
        assert serialized["success"] is True
        assert serialized["message"] == "Платеж успешно обработан"
        assert serialized["transaction_id"] == "test-tx-123"

    def test_webhook_request_validation(self):
        """Тест валидации запроса вебхука"""
        # Валидные данные
        valid_data = {
            "transaction_id": "tx-123",
            "user_id": 1,
            "account_id": 2,
            "amount": 150.50,
            "signature": "test_signature"
        }
        
        request = WebhookRequest(**valid_data)
        assert request.transaction_id == "tx-123"
        assert request.user_id == 1
        assert request.account_id == 2
        assert request.amount == Decimal("150.50")
        assert request.signature == "test_signature"

        # Невалидные данные - отрицательная сумма
        with pytest.raises(ValueError):
            WebhookRequest(
                transaction_id="tx-123",
                user_id=1,
                account_id=2,
                amount=-100,
                signature="test"
            )
