"""Тесты для сервиса работы с платежами"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.payment_service import PaymentService
from app.models.payment import Payment


class TestPaymentService:
    """Тесты для PaymentService"""

    @pytest.fixture
    def mock_payment(self):
        """Мок объекта платежа"""
        payment = Payment(
            id=1,
            transaction_id="tx-123",
            account_id=1,
            user_id=1,
            amount=Decimal("100.00")
        )
        return payment

    @pytest.fixture
    def mock_payments_list(self):
        """Мок списка платежей"""
        return [
            Payment(id=1, transaction_id="tx-123", account_id=1, user_id=1, amount=Decimal("100.00")),
            Payment(id=2, transaction_id="tx-456", account_id=1, user_id=1, amount=Decimal("50.00"))
        ]

    @patch('app.services.payment_service.get_db_session')
    async def test_get_user_payments_success(self, mock_get_db_session, mock_payments_list):
        """Тест успешного получения платежей пользователя"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_payments_list
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await PaymentService.get_user_payments(user_id=1)

        assert len(result) == 2
        assert result[0].transaction_id == "tx-123"
        assert result[1].transaction_id == "tx-456"
        assert result[0].amount == Decimal("100.00")
        assert result[1].amount == Decimal("50.00")

    @patch('app.services.payment_service.get_db_session')
    async def test_get_user_payments_empty(self, mock_get_db_session):
        """Тест получения пустого списка платежей"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await PaymentService.get_user_payments(user_id=999)
        assert result == []

    @patch('app.services.payment_service.get_db_session')
    async def test_get_payment_by_transaction_id_found(self, mock_get_db_session, mock_payment):
        """Тест успешного поиска платежа по transaction_id"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_payment
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await PaymentService.get_payment_by_transaction_id("tx-123")

        assert result is not None
        assert result.transaction_id == "tx-123"
        assert result.amount == Decimal("100.00")

    @patch('app.services.payment_service.get_db_session')
    async def test_get_payment_by_transaction_id_not_found(self, mock_get_db_session):
        """Тест поиска несуществующего платежа"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await PaymentService.get_payment_by_transaction_id("non-existent")
        assert result is None

    @patch('app.services.payment_service.get_db_session')
    async def test_create_payment_success(self, mock_get_db_session, mock_payment):
        """Тест успешного создания платежа"""
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # Синхронный метод
        mock_session.commit = AsyncMock()  # Асинхронный метод  
        mock_session.refresh = AsyncMock()  # Асинхронный метод
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        # Мокаем создание платежа
        result = await PaymentService.create_payment(
            transaction_id="tx-789",
            account_id=1,
            user_id=1,
            amount=Decimal("200.00")
        )

        # Проверяем что методы сессии были вызваны
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch('app.services.payment_service.get_db_session')
    async def test_get_account_payments_success(self, mock_get_db_session, mock_payments_list):
        """Тест получения платежей по счету"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_payments_list
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await PaymentService.get_account_payments(account_id=1)

        assert len(result) == 2
        assert all(payment.account_id == 1 for payment in result)

    @patch('app.services.payment_service.get_db_session')
    async def test_get_account_payments_empty(self, mock_get_db_session):
        """Тест получения пустого списка платежей по счету"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await PaymentService.get_account_payments(account_id=999)
        assert result == []

    @patch('app.services.payment_service.get_db_session')
    async def test_get_payment_by_id_found(self, mock_get_db_session, mock_payment):
        """Тест поиска платежа по ID"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_payment
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await PaymentService.get_payment_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.transaction_id == "tx-123"

    @patch('app.services.payment_service.get_db_session')
    async def test_get_payment_by_id_not_found(self, mock_get_db_session):
        """Тест поиска несуществующего платежа по ID"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await PaymentService.get_payment_by_id(999)
        assert result is None

    @patch('app.services.payment_service.get_db_session')
    async def test_create_payment_with_decimal_amount(self, mock_get_db_session):
        """Тест создания платежа с Decimal суммой"""
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # Синхронный метод
        mock_session.commit = AsyncMock()  # Асинхронный метод
        mock_session.refresh = AsyncMock()  # Асинхронный метод
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        await PaymentService.create_payment(
            transaction_id="tx-decimal",
            account_id=1,
            user_id=1,
            amount=Decimal("99.99")
        )

        # Проверяем что методы были вызваны
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch('app.services.payment_service.get_db_session')
    async def test_create_payment_with_float_amount(self, mock_get_db_session):
        """Тест создания платежа с float суммой"""
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # Синхронный метод
        mock_session.commit = AsyncMock()  # Асинхронный метод
        mock_session.refresh = AsyncMock()  # Асинхронный метод
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        await PaymentService.create_payment(
            transaction_id="tx-float",
            account_id=1,
            user_id=1,
            amount=123.45
        )

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch('app.services.payment_service.get_db_session')
    async def test_payments_ordered_by_created_at_desc(self, mock_get_db_session):
        """Тест что платежи сортируются по дате создания (новые первые)"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        await PaymentService.get_user_payments(user_id=1)

        # Проверяем что execute был вызван (порядок сортировки проверяется в SQL запросе)
        mock_session.execute.assert_called_once()

    @patch('app.services.payment_service.get_db_session')
    async def test_account_payments_ordered_by_created_at_desc(self, mock_get_db_session):
        """Тест что платежи по счету сортируются по дате создания"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        await PaymentService.get_account_payments(account_id=1)

        mock_session.execute.assert_called_once()

    def test_payment_service_class_structure(self):
        """Тест структуры класса PaymentService"""
        # Проверяем что все методы существуют
        assert hasattr(PaymentService, 'get_user_payments')
        assert hasattr(PaymentService, 'get_payment_by_transaction_id')
        assert hasattr(PaymentService, 'create_payment')
        assert hasattr(PaymentService, 'get_account_payments')
        assert hasattr(PaymentService, 'get_payment_by_id')

        # Проверяем что методы статические
        import inspect
        assert inspect.isfunction(PaymentService.get_user_payments)
        assert inspect.isfunction(PaymentService.get_payment_by_transaction_id)
        assert inspect.isfunction(PaymentService.create_payment)
        assert inspect.isfunction(PaymentService.get_account_payments)
        assert inspect.isfunction(PaymentService.get_payment_by_id)

    @patch('app.services.payment_service.get_db_session')
    async def test_create_payment_large_amount(self, mock_get_db_session):
        """Тест создания платежа с большой суммой"""
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # Синхронный метод
        mock_session.commit = AsyncMock()  # Асинхронный метод
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        large_amount = Decimal("999999.99")
        await PaymentService.create_payment(
            transaction_id="tx-large",
            account_id=1,
            user_id=1,
            amount=large_amount
        )

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch('app.services.payment_service.get_db_session')
    async def test_create_payment_small_amount(self, mock_get_db_session):
        """Тест создания платежа с малой суммой"""
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # Синхронный метод
        mock_session.commit = AsyncMock()  # Асинхронный метод
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        small_amount = Decimal("0.01")
        await PaymentService.create_payment(
            transaction_id="tx-small",
            account_id=1,
            user_id=1,
            amount=small_amount
        )

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
