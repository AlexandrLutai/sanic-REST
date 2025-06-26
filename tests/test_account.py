import pytest
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.account import Account
from app.models.user import User
from app.models.base import Base


class TestAccountModel:
    """Тесты для модели Account"""

    @pytest.fixture
    async def test_engine(self):
        """Тестовый движок с SQLite в памяти"""
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        yield engine
        await engine.dispose()

    @pytest.fixture
    async def test_session(self, test_engine):
        """Тестовая сессия"""
        AsyncSessionLocal = sessionmaker(
            bind=test_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        async with AsyncSessionLocal() as session:
            yield session

    @pytest.fixture
    async def test_user(self, test_session):
        """Тестовый пользователь"""
        user = User(
            email="testuser@example.com",
            password_hash="hash",
            full_name="Test User"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        return user

    def test_account_creation(self, test_user):
        """Тест создания объекта Account"""
        account = Account(
            user_id=test_user.id,
            account_number="1234567890123456",
            balance=1000.50,
            currency="USD"
        )
        
        assert account.user_id == test_user.id
        assert account.account_number == "1234567890123456"
        assert account.balance == 1000.50
        assert account.currency == "USD"

    def test_account_defaults(self, test_user):
        """Тест значений по умолчанию"""
        account = Account(
            user_id=test_user.id,
            account_number="1234567890123456"
        )
        
        # Default значения устанавливаются в __init__
        assert account.balance == Decimal('0.00')
        assert account.currency == "RUB"

    def test_account_tablename(self):
        """Тест имени таблицы Account"""
        assert Account.__tablename__ == "accounts"

    def test_account_repr(self, test_user):
        """Тест строкового представления Account"""
        account = Account(
            id=1,
            user_id=test_user.id,
            account_number="1234567890123456",
            balance=1500.25,
            currency="EUR"
        )
        
        expected_repr = "<Account(id=1, account_number='1234567890123456', balance=1500.25, currency='EUR')>"
        assert repr(account) == expected_repr

    def test_account_to_dict(self, test_user):
        """Тест конвертации Account в словарь"""
        test_time = datetime.now()
        
        account = Account(
            id=1,
            user_id=test_user.id,
            account_number="1234567890123456",
            balance=2000.75,
            currency="USD"
        )
        account.created_at = test_time
        account.updated_at = test_time
        
        data = account.to_dict()
        
        assert data['id'] == "1"
        assert data['user_id'] == str(test_user.id)
        assert data['account_number'] == "1234567890123456"
        assert data['balance'] == 2000.75
        assert data['currency'] == "USD"
        assert data['created_at'] == test_time.isoformat()
        assert data['updated_at'] == test_time.isoformat()

    def test_add_funds_success(self, test_user):
        """Тест успешного пополнения баланса"""
        account = Account(
            user_id=test_user.id,
            account_number="1234567890123456",
            balance=100.00
        )
        
        account.add_funds(50.25)
        assert account.balance == 150.25

    def test_add_funds_zero_amount(self, test_user):
        """Тест пополнения на нулевую сумму"""
        account = Account(
            user_id=test_user.id,
            account_number="1234567890123456",
            balance=100.00
        )
        
        with pytest.raises(ValueError, match="Сумма пополнения должна быть положительной"):
            account.add_funds(0)

    def test_add_funds_negative_amount(self, test_user):
        """Тест пополнения на отрицательную сумму"""
        account = Account(
            user_id=test_user.id,
            account_number="1234567890123456",
            balance=100.00
        )
        
        with pytest.raises(ValueError, match="Сумма пополнения должна быть положительной"):
            account.add_funds(-10.50)

    def test_withdraw_funds_success(self, test_user):
        """Тест успешного списания средств"""
        account = Account(
            user_id=test_user.id,
            account_number="1234567890123456",
            balance=100.00
        )
        
        account.withdraw_funds(30.50)
        assert account.balance == 69.50

    def test_withdraw_funds_insufficient_balance(self, test_user):
        """Тест списания при недостатке средств"""
        account = Account(
            user_id=test_user.id,
            account_number="1234567890123456",
            balance=50.00
        )
        
        with pytest.raises(ValueError, match="Недостаточно средств на счете"):
            account.withdraw_funds(100.00)

    def test_withdraw_funds_zero_amount(self, test_user):
        """Тест списания нулевой суммы"""
        account = Account(
            user_id=test_user.id,
            account_number="1234567890123456",
            balance=100.00
        )
        
        with pytest.raises(ValueError, match="Сумма списания должна быть положительной"):
            account.withdraw_funds(0)

    def test_withdraw_funds_negative_amount(self, test_user):
        """Тест списания отрицательной суммы"""
        account = Account(
            user_id=test_user.id,
            account_number="1234567890123456",
            balance=100.00
        )
        
        with pytest.raises(ValueError, match="Сумма списания должна быть положительной"):
            account.withdraw_funds(-25.00)

    def test_has_sufficient_balance_true(self, test_user):
        """Тест проверки достаточности средств - положительный"""
        account = Account(
            user_id=test_user.id,
            account_number="1234567890123456",
            balance=100.00
        )
        
        assert account.has_sufficient_balance(50.00) is True
        assert account.has_sufficient_balance(100.00) is True

    def test_has_sufficient_balance_false(self, test_user):
        """Тест проверки достаточности средств - отрицательный"""
        account = Account(
            user_id=test_user.id,
            account_number="1234567890123456",
            balance=50.00
        )
        
        assert account.has_sufficient_balance(75.00) is False
        assert account.has_sufficient_balance(100.00) is False

    async def test_account_database_operations(self, test_session, test_user):
        """Тест операций с Account в базе данных"""
        account = Account(
            user_id=test_user.id,
            account_number="9876543210987654",
            balance=500.00,
            currency="EUR"
        )
        
        test_session.add(account)
        await test_session.commit()
        await test_session.refresh(account)
        
        assert account.id is not None
        assert isinstance(account.id, int)
        assert account.user_id == test_user.id
        assert account.created_at is not None
        assert account.updated_at is not None

    async def test_account_unique_account_number(self, test_session, test_user):
        """Тест уникальности номера счета"""
        account1 = Account(
            user_id=test_user.id,
            account_number="1111222233334444",
            balance=100.00
        )
        account2 = Account(
            user_id=test_user.id,
            account_number="1111222233334444",
            balance=200.00
        )
        
        test_session.add(account1)
        await test_session.commit()
        
        test_session.add(account2)
        
        with pytest.raises(Exception):
            await test_session.commit()

    async def test_account_relationship_with_user(self, test_session, test_user):
        """Тест связи Account с User"""
        account = Account(
            user_id=test_user.id,
            account_number="5555666677778888",
            balance=750.00
        )
        
        test_session.add(account)
        await test_session.commit()
        await test_session.refresh(account)
        
        # Проверяем что можем получить пользователя через связь
        assert account.user is not None
        assert account.user.id == test_user.id
        assert account.user.email == test_user.email

    async def test_user_accounts_relationship(self, test_session, test_user):
        """Тест получения счетов пользователя через relationship"""
        accounts = [
            Account(user_id=test_user.id, account_number="1111111111111111", balance=100.00),
            Account(user_id=test_user.id, account_number="2222222222222222", balance=200.00),
            Account(user_id=test_user.id, account_number="3333333333333333", balance=300.00),
        ]
        
        test_session.add_all(accounts)
        await test_session.commit()
        
        # Обновляем пользователя чтобы загрузить связанные счета
        await test_session.refresh(test_user)
        
        assert len(test_user.accounts) == 3
        account_numbers = [acc.account_number for acc in test_user.accounts]
        assert "1111111111111111" in account_numbers
        assert "2222222222222222" in account_numbers
        assert "3333333333333333" in account_numbers

    async def test_account_update_balance(self, test_session, test_user):
        """Тест обновления баланса счета"""
        account = Account(
            user_id=test_user.id,
            account_number="4444555566667777",
            balance=1000.00
        )
        
        test_session.add(account)
        await test_session.commit()
        await test_session.refresh(account)
        
        # Обновляем баланс
        account.add_funds(250.50)
        await test_session.commit()
        await test_session.refresh(account)
        
        assert account.balance == 1250.50

    async def test_multiple_accounts_for_user(self, test_session, test_user):
        """Тест создания нескольких счетов у одного пользователя"""
        accounts = [
            Account(user_id=test_user.id, account_number="1001001001001001", balance=100.00, currency="RUB"),
            Account(user_id=test_user.id, account_number="2002002002002002", balance=200.00, currency="USD"),
            Account(user_id=test_user.id, account_number="3003003003003003", balance=300.00, currency="EUR"),
        ]
        
        test_session.add_all(accounts)
        await test_session.commit()
        
        from sqlalchemy import select
        result = await test_session.execute(
            select(Account).where(Account.user_id == test_user.id)
        )
        user_accounts = result.scalars().all()
        
        assert len(user_accounts) == 3
        
        currencies = [acc.currency for acc in user_accounts]
        assert "RUB" in currencies
        assert "USD" in currencies
        assert "EUR" in currencies
