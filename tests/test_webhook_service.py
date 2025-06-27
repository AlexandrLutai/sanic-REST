"""Тесты для сервиса обработки вебхуков"""

import pytest
import hashlib
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from app.services.webhook_service import WebhookService
from app.models.user import User
from app.models.account import Account
from app.models.payment import Payment


class TestWebhookService:
    """Тесты для WebhookService"""

    @pytest.fixture
    def valid_webhook_data(self):
        """Валидные данные вебхука"""
        return {
            "account_id": 1,
            "amount": "100",
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "user_id": 1
        }

    @pytest.fixture
    def secret_key(self):
        """Секретный ключ"""
        return "gfdmhghif38yrf9ew0jkf32"

    @pytest.fixture
    def mock_user(self):
        """Мок пользователя"""
        return User(id=1, email="test@example.com", full_name="Test User")

    @pytest.fixture
    def mock_account(self):
        """Мок счета"""
        return Account(id=1, user_id=1, balance=Decimal("50.00"))

    @pytest.fixture
    def mock_payment(self):
        """Мок платежа"""
        return Payment(
            id=1,
            transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
            account_id=1,
            user_id=1,
            amount=Decimal("100.00")
        )

    def test_verify_signature_valid(self, valid_webhook_data, secret_key):
        """Тест корректной проверки подписи"""
        # Вычисляем правильную подпись
        signature_string = f"{valid_webhook_data['account_id']}{valid_webhook_data['amount']}{valid_webhook_data['transaction_id']}{valid_webhook_data['user_id']}{secret_key}"
        correct_signature = hashlib.sha256(signature_string.encode()).hexdigest()

        result = WebhookService.verify_signature(valid_webhook_data, secret_key, correct_signature)
        assert result is True

    def test_verify_signature_invalid(self, valid_webhook_data, secret_key):
        """Тест неверной подписи"""
        wrong_signature = "wrong_signature_hash"

        result = WebhookService.verify_signature(valid_webhook_data, secret_key, wrong_signature)
        assert result is False

    def test_verify_signature_readme_example(self):
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

    def test_verify_signature_wrong_secret_key(self, valid_webhook_data):
        """Тест с неправильным секретным ключом"""
        correct_secret = "correct_secret"
        wrong_secret = "wrong_secret"

        # Генерируем подпись с правильным ключом
        signature_string = f"{valid_webhook_data['account_id']}{valid_webhook_data['amount']}{valid_webhook_data['transaction_id']}{valid_webhook_data['user_id']}{correct_secret}"
        signature = hashlib.sha256(signature_string.encode()).hexdigest()

        # Проверяем с неправильным ключом
        result = WebhookService.verify_signature(valid_webhook_data, wrong_secret, signature)
        assert result is False

    def test_verify_signature_alphabetical_order(self):
        """Тест правильного порядка полей в подписи"""
        data = {
            "account_id": 5,
            "amount": "250.50",
            "transaction_id": "test-tx-id",
            "user_id": 10
        }
        secret_key = "test_secret"

        # Проверяем порядок: account_id, amount, transaction_id, user_id
        expected_string = "5250.50test-tx-id10test_secret"
        expected_signature = hashlib.sha256(expected_string.encode()).hexdigest()

        result = WebhookService.verify_signature(data, secret_key, expected_signature)
        assert result is True

    @patch('app.services.webhook_service.PaymentService.get_payment_by_transaction_id')
    @patch('app.services.webhook_service.UserService.get_user_by_id')
    @patch('app.services.webhook_service.AccountService.get_account_by_id')
    @patch('app.services.webhook_service.PaymentService.create_payment')
    @patch('app.services.webhook_service.AccountService.add_to_balance')
    async def test_process_payment_success_existing_account(
        self, mock_add_balance, mock_create_payment, mock_get_account, 
        mock_get_user, mock_get_payment, mock_user, mock_account, mock_payment
    ):
        """Тест успешной обработки платежа с существующим счетом"""
        # Настраиваем моки
        mock_get_payment.return_value = None  # Транзакция уникальна
        mock_get_user.return_value = mock_user  # Пользователь существует
        mock_get_account.return_value = mock_account  # Счет существует
        mock_create_payment.return_value = mock_payment
        mock_add_balance.return_value = mock_account

        # Данные для обработки
        result = await WebhookService.process_payment(
            transaction_id="tx-123",
            account_id=1,
            user_id=1,
            amount=Decimal("100.00"),
            signature="a51258ef048f88f73b4e12050496f4e065351c3cc7bdf688713a8efc839270bc",
            secret_key="gfdmhghif38yrf9ew0jkf32"
        )

        # Проверяем результат
        assert result["success"] is True
        assert result["message"] == "Платеж успешно обработан"
        assert "payment_id" in result

    async def test_process_payment_invalid_signature(self):
        """Тест обработки с неверной подписью"""
        result = await WebhookService.process_payment(
            transaction_id="tx-123",
            account_id=1,
            user_id=1,
            amount=Decimal("100.00"),
            signature="wrong_signature",
            secret_key="test_secret"
        )

        assert result["success"] is False
        assert result["error_code"] == "INVALID_SIGNATURE"
        assert result["message"] == "Неверная подпись"

    @patch('app.services.webhook_service.PaymentService.get_payment_by_transaction_id')
    async def test_process_payment_duplicate_transaction(self, mock_get_payment, mock_payment):
        """Тест обработки дублирующейся транзакции"""
        mock_get_payment.return_value = mock_payment  # Транзакция уже существует

        # Используем правильную подпись
        result = await WebhookService.process_payment(
            transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
            account_id=1,
            user_id=1,
            amount=Decimal("100"),
            signature="7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8",
            secret_key="gfdmhghif38yrf9ew0jkf32"
        )

        assert result["success"] is False
        assert result["error_code"] == "DUPLICATE_TRANSACTION"
        assert result["message"] == "Транзакция уже обработана"

    @patch('app.services.webhook_service.PaymentService.get_payment_by_transaction_id')
    @patch('app.services.webhook_service.UserService.get_user_by_id')
    async def test_process_payment_user_not_found(self, mock_get_user, mock_get_payment):
        """Тест обработки с несуществующим пользователем"""
        mock_get_payment.return_value = None  # Транзакция уникальна
        mock_get_user.return_value = None  # Пользователь не найден

        result = await WebhookService.process_payment(
            transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
            account_id=1,
            user_id=999,
            amount=Decimal("100"),
            signature="01073c9d973ee2413c72f99a9eb886111c2747b9aa709bbe84dd8229e2b7b1f8",  # Подпись для user_id=999
            secret_key="gfdmhghif38yrf9ew0jkf32"
        )

        assert result["success"] is False
        assert result["error_code"] == "USER_NOT_FOUND"
        assert result["message"] == "Пользователь не найден"

    @patch('app.services.webhook_service.PaymentService.get_payment_by_transaction_id')
    @patch('app.services.webhook_service.UserService.get_user_by_id')
    @patch('app.services.webhook_service.AccountService.get_account_by_id')
    @patch('app.services.webhook_service.AccountService.create_account')
    @patch('app.services.webhook_service.PaymentService.create_payment')
    @patch('app.services.webhook_service.AccountService.add_to_balance')
    async def test_process_payment_create_new_account(
        self, mock_add_balance, mock_create_payment, mock_create_account,
        mock_get_account, mock_get_user, mock_get_payment, mock_user, mock_account, mock_payment
    ):
        """Тест создания нового счета при обработке платежа"""
        mock_get_payment.return_value = None
        mock_get_user.return_value = mock_user
        mock_get_account.return_value = None  # Счет не существует
        mock_create_account.return_value = mock_account  # Создаем новый счет
        mock_create_payment.return_value = mock_payment
        mock_add_balance.return_value = mock_account

        result = await WebhookService.process_payment(
            transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
            account_id=1,
            user_id=1,
            amount=Decimal("100"),
            signature="7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8",
            secret_key="gfdmhghif38yrf9ew0jkf32"
        )

        assert result["success"] is True
        mock_create_account.assert_called_once_with(user_id=1, account_id=1)

    @patch('app.services.webhook_service.PaymentService.get_payment_by_transaction_id')
    @patch('app.services.webhook_service.UserService.get_user_by_id')
    @patch('app.services.webhook_service.AccountService.get_account_by_id')
    async def test_process_payment_account_ownership_error(self, mock_get_account, mock_get_user, mock_get_payment, mock_user):
        """Тест ошибки принадлежности счета"""
        wrong_account = Account(id=1, user_id=2, balance=Decimal("50.00"))  # Счет другого пользователя
        
        mock_get_payment.return_value = None
        mock_get_user.return_value = mock_user
        mock_get_account.return_value = wrong_account

        result = await WebhookService.process_payment(
            transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
            account_id=1,
            user_id=1,
            amount=Decimal("100"),
            signature="7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8",
            secret_key="gfdmhghif38yrf9ew0jkf32"
        )

        assert result["success"] is False
        assert result["error_code"] == "ACCOUNT_OWNERSHIP_ERROR"
        assert result["message"] == "Счет не принадлежит пользователю"

    @patch('app.services.webhook_service.PaymentService.get_payment_by_transaction_id')
    @patch('app.services.webhook_service.UserService.get_user_by_id')
    @patch('app.services.webhook_service.AccountService.get_account_by_id')
    @patch('app.services.webhook_service.AccountService.create_account')
    async def test_process_payment_account_creation_error(
        self, mock_create_account, mock_get_account, mock_get_user, mock_get_payment, mock_user
    ):
        """Тест ошибки создания счета"""
        mock_get_payment.return_value = None
        mock_get_user.return_value = mock_user
        mock_get_account.return_value = None
        mock_create_account.side_effect = Exception("Database error")

        result = await WebhookService.process_payment(
            transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
            account_id=1,
            user_id=1,
            amount=Decimal("100"),
            signature="7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8",
            secret_key="gfdmhghif38yrf9ew0jkf32"
        )

        assert result["success"] is False
        assert result["error_code"] == "ACCOUNT_CREATION_ERROR"
        assert "Database error" in result["message"]

    @patch('app.services.webhook_service.PaymentService.get_payment_by_transaction_id')
    @patch('app.services.webhook_service.UserService.get_user_by_id')
    @patch('app.services.webhook_service.AccountService.get_account_by_id')
    @patch('app.services.webhook_service.PaymentService.create_payment')
    async def test_process_payment_creation_error(
        self, mock_create_payment, mock_get_account, mock_get_user, mock_get_payment, 
        mock_user, mock_account
    ):
        """Тест ошибки создания платежа"""
        mock_get_payment.return_value = None
        mock_get_user.return_value = mock_user
        mock_get_account.return_value = mock_account
        mock_create_payment.side_effect = Exception("Payment creation failed")

        result = await WebhookService.process_payment(
            transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
            account_id=1,
            user_id=1,
            amount=Decimal("100"),
            signature="7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8",
            secret_key="gfdmhghif38yrf9ew0jkf32"
        )

        assert result["success"] is False
        assert result["error_code"] == "PAYMENT_CREATION_ERROR"
        assert "Payment creation failed" in result["message"]

    @patch('app.services.webhook_service.PaymentService.get_payment_by_transaction_id')
    @patch('app.services.webhook_service.UserService.get_user_by_id')
    @patch('app.services.webhook_service.AccountService.get_account_by_id')
    @patch('app.services.webhook_service.PaymentService.create_payment')
    @patch('app.services.webhook_service.AccountService.add_to_balance')
    async def test_process_payment_balance_update_error(
        self, mock_add_balance, mock_create_payment, mock_get_account, 
        mock_get_user, mock_get_payment, mock_user, mock_account, mock_payment
    ):
        """Тест ошибки начисления средств"""
        mock_get_payment.return_value = None
        mock_get_user.return_value = mock_user
        mock_get_account.return_value = mock_account
        mock_create_payment.return_value = mock_payment
        mock_add_balance.side_effect = Exception("Balance update failed")

        result = await WebhookService.process_payment(
            transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
            account_id=1,
            user_id=1,
            amount=Decimal("100"),
            signature="7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8",
            secret_key="gfdmhghif38yrf9ew0jkf32"
        )

        assert result["success"] is False
        assert result["error_code"] == "BALANCE_UPDATE_ERROR"
        assert "Balance update failed" in result["message"]

    def test_webhook_service_class_structure(self):
        """Тест структуры класса WebhookService"""
        assert hasattr(WebhookService, 'verify_signature')
        assert hasattr(WebhookService, 'process_payment')

        # Проверяем что методы статические
        import inspect
        assert inspect.isfunction(WebhookService.verify_signature)
        assert inspect.isfunction(WebhookService.process_payment)
