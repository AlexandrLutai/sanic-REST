"""Тесты для сервиса работы со счетами"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.account_service import AccountService
from app.models.account import Account


class TestAccountService:
    """Тесты для AccountService"""

    @pytest.fixture
    def mock_account(self):
        """Мок объекта счета"""
        account = Account(
            id=1,
            user_id=1,
            balance=Decimal("100.00")
        )
        return account

    @pytest.fixture
    def mock_accounts_list(self):
        """Мок списка счетов"""
        return [
            Account(id=1, user_id=1, balance=Decimal("100.00")),
            Account(id=2, user_id=1, balance=Decimal("250.50"))
        ]

    @patch('app.services.account_service.get_db_session')
    async def test_get_user_accounts_success(self, mock_get_db_session, mock_accounts_list):
        """Тест успешного получения счетов пользователя"""
        # Настраиваем мок сессии
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_accounts_list
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        # Вызываем метод
        result = await AccountService.get_user_accounts(user_id=1)

        # Проверяем результат
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2
        assert result[0].balance == Decimal("100.00")
        assert result[1].balance == Decimal("250.50")

    @patch('app.services.account_service.get_db_session')
    async def test_get_user_accounts_empty(self, mock_get_db_session):
        """Тест получения пустого списка счетов"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await AccountService.get_user_accounts(user_id=999)
        assert result == []

    @patch('app.services.account_service.get_db_session')
    async def test_get_account_by_id_found(self, mock_get_db_session, mock_account):
        """Тест успешного получения счета по ID"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_account  # Обычный return_value
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await AccountService.get_account_by_id(account_id=1)

        assert result is not None
        assert result.id == 1
        assert result.user_id == 1
        assert result.balance == Decimal("100.00")

    @patch('app.services.account_service.get_db_session')
    async def test_get_account_by_id_not_found(self, mock_get_db_session):
        """Тест получения несуществующего счета"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # Обычный return_value
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await AccountService.get_account_by_id(account_id=999)
        assert result is None

    @patch('app.services.account_service.get_db_session')
    async def test_create_account_success(self, mock_get_db_session):
        """Тест успешного создания счета"""
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # Синхронный метод
        mock_session.commit = AsyncMock()  # Асинхронный метод
        mock_session.refresh = AsyncMock()  # Асинхронный метод
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        # Создаем новый счет
        result = await AccountService.create_account(user_id=1)

        # Проверяем что методы сессии были вызваны
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch('app.services.account_service.get_db_session')
    async def test_create_account_with_specific_id(self, mock_get_db_session):
        """Тест создания счета с конкретным ID"""
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # Синхронный метод
        mock_session.commit = AsyncMock()  # Асинхронный метод
        mock_session.refresh = AsyncMock()  # Асинхронный метод
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await AccountService.create_account(user_id=1, account_id=5)

        # Проверяем что методы сессии были вызваны
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch('app.services.account_service.get_db_session')
    async def test_add_to_balance_success(self, mock_get_db_session, mock_account):
        """Тест успешного пополнения баланса"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_account
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        # Пополняем баланс
        result = await AccountService.add_to_balance(account_id=1, amount=Decimal("50.00"))

        # Проверяем что баланс увеличился
        assert mock_account.balance == Decimal("150.00")  # 100 + 50
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch('app.services.account_service.get_db_session')
    async def test_add_to_balance_account_not_found(self, mock_get_db_session):
        """Тест пополнения баланса несуществующего счета"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # Счет не найден
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        # Пытаемся пополнить несуществующий счет
        with pytest.raises(ValueError, match="Счет не найден"):
            await AccountService.add_to_balance(account_id=999, amount=Decimal("50.00"))

    @patch('app.services.account_service.get_db_session')
    async def test_get_account_by_user_and_id_found(self, mock_get_db_session, mock_account):
        """Тест поиска счета по пользователю и ID"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_account
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await AccountService.get_account_by_user_and_id(user_id=1, account_id=1)

        assert result is not None
        assert result.id == 1
        assert result.user_id == 1

    @patch('app.services.account_service.get_db_session')
    async def test_get_account_by_user_and_id_not_found(self, mock_get_db_session):
        """Тест поиска несуществующего счета по пользователю и ID"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # Счет не найден
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        result = await AccountService.get_account_by_user_and_id(user_id=1, account_id=999)
        assert result is None

    @patch('app.services.account_service.get_db_session')
    async def test_add_decimal_amount(self, mock_get_db_session, mock_account):
        """Тест пополнения с Decimal суммой"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_account
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        # Пополняем баланс с Decimal
        await AccountService.add_to_balance(account_id=1, amount=Decimal("75.25"))

        # Проверяем точность Decimal
        assert mock_account.balance == Decimal("175.25")

    @patch('app.services.account_service.get_db_session')
    async def test_add_float_amount(self, mock_get_db_session, mock_account):
        """Тест пополнения с float суммой"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_account
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db_session.return_value.__aenter__.return_value = mock_session

        # Пополняем баланс с float
        await AccountService.add_to_balance(account_id=1, amount=25.50)

        # Проверяем что сумма добавилась
        assert mock_account.balance == Decimal("125.50")

    def test_account_service_class_structure(self):
        """Тест структуры класса AccountService"""
        # Проверяем что все методы существуют
        assert hasattr(AccountService, 'get_user_accounts')
        assert hasattr(AccountService, 'get_account_by_id')
        assert hasattr(AccountService, 'create_account')
        assert hasattr(AccountService, 'add_to_balance')
        assert hasattr(AccountService, 'get_account_by_user_and_id')

        # Проверяем что методы статические
        import inspect
        assert inspect.isfunction(AccountService.get_user_accounts)
        assert inspect.isfunction(AccountService.get_account_by_id)
        assert inspect.isfunction(AccountService.create_account)
        assert inspect.isfunction(AccountService.add_to_balance)
        assert inspect.isfunction(AccountService.get_account_by_user_and_id)
