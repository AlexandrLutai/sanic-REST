import pytest
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.payment import Payment, PaymentStatus, PaymentType
from app.models.account import Account
from app.models.user import User
from app.models.base import Base


class TestPaymentModel:
    """Тесты для модели Payment"""

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

    @pytest.fixture
    async def test_account(self, test_session, test_user):
        """Тестовый счет"""
        account = Account(
            user_id=test_user.id,
            account_number="1234567890123456",
            balance=1000.00,
            currency="RUB"
        )
        test_session.add(account)
        await test_session.commit()
        await test_session.refresh(account)
        return account

    @pytest.fixture
    async def test_account2(self, test_session, test_user):
        """Второй тестовый счет для переводов"""
        account = Account(
            user_id=test_user.id,
            account_number="9876543210987654",
            balance=500.00,
            currency="RUB"
        )
        test_session.add(account)
        await test_session.commit()
        await test_session.refresh(account)
        return account

    def test_payment_creation(self, test_user, test_account):
        """Тест создания объекта Payment"""
        payment = Payment(
            transaction_id="test-tx-123",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=100.50,
            currency="USD",
            payment_type=PaymentType.DEPOSIT,
            status=PaymentStatus.PENDING
        )
        
        assert payment.transaction_id == "test-tx-123"
        assert payment.account_id == test_account.id
        assert payment.user_id == test_user.id
        assert payment.amount == Decimal('100.50')
        assert payment.currency == "USD"
        assert payment.payment_type == PaymentType.DEPOSIT
        assert payment.status == PaymentStatus.PENDING

    def test_payment_defaults(self, test_user, test_account):
        """Тест значений по умолчанию"""
        payment = Payment(
            transaction_id="test-tx-456",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=50.00
        )
        
        assert payment.currency == "RUB"
        assert payment.payment_type == PaymentType.DEPOSIT
        assert payment.status == PaymentStatus.PENDING
        assert payment.description is None

    def test_payment_tablename(self):
        """Тест имени таблицы Payment"""
        assert Payment.__tablename__ == "payments"

    def test_payment_repr(self, test_user, test_account):
        """Тест строкового представления Payment"""
        payment = Payment(
            id=1,
            transaction_id="test-tx-789",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=250.75,
            status=PaymentStatus.COMPLETED
        )
        
        expected_repr = "<Payment(id=1, transaction_id='test-tx-789', amount=250.75, status='completed')>"
        assert repr(payment) == expected_repr

    def test_payment_to_dict(self, test_user, test_account):
        """Тест конвертации Payment в словарь"""
        test_time = datetime.now()
        
        payment = Payment(
            id=1,
            transaction_id="test-tx-999",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=300.25,
            currency="EUR",
            payment_type=PaymentType.WITHDRAWAL,
            status=PaymentStatus.FAILED,
            description="Test payment",
            external_data='{"source": "test"}'
        )
        payment.created_at = test_time
        payment.updated_at = test_time
        
        data = payment.to_dict()
        
        assert data['id'] == "1"
        assert data['transaction_id'] == "test-tx-999"
        assert data['account_id'] == str(test_account.id)
        assert data['user_id'] == str(test_user.id)
        assert data['amount'] == 300.25
        assert data['currency'] == "EUR"
        assert data['payment_type'] == "withdrawal"
        assert data['status'] == "failed"
        assert data['description'] == "Test payment"
        assert data['external_data'] == '{"source": "test"}'
        assert data['target_account_id'] is None
        assert data['created_at'] == test_time.isoformat()
        assert data['updated_at'] == test_time.isoformat()

    def test_payment_status_checks(self, test_user, test_account):
        """Тест методов проверки статуса"""
        payment = Payment(
            transaction_id="test-status",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=100.00,
            status=PaymentStatus.PENDING
        )
        
        assert payment.is_pending() is True
        assert payment.is_completed() is False
        assert payment.is_failed() is False
        assert payment.can_be_processed() is True
        assert payment.can_be_cancelled() is True

    def test_payment_status_completed(self, test_user, test_account):
        """Тест статуса completed"""
        payment = Payment(
            transaction_id="test-completed",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=100.00,
            status=PaymentStatus.COMPLETED
        )
        
        assert payment.is_pending() is False
        assert payment.is_completed() is True
        assert payment.is_failed() is False
        assert payment.can_be_processed() is False
        assert payment.can_be_cancelled() is False

    def test_payment_status_failed(self, test_user, test_account):
        """Тест статуса failed"""
        payment = Payment(
            transaction_id="test-failed",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=100.00,
            status=PaymentStatus.FAILED
        )
        
        assert payment.is_pending() is False
        assert payment.is_completed() is False
        assert payment.is_failed() is True
        assert payment.can_be_processed() is False
        assert payment.can_be_cancelled() is True

    def test_mark_completed_success(self, test_user, test_account):
        """Тест успешного завершения платежа"""
        payment = Payment(
            transaction_id="test-complete",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=100.00,
            status=PaymentStatus.PENDING
        )
        
        payment.mark_completed()
        assert payment.status == PaymentStatus.COMPLETED

    def test_mark_completed_invalid_status(self, test_user, test_account):
        """Тест завершения платежа с неверным статусом"""
        payment = Payment(
            transaction_id="test-complete-invalid",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=100.00,
            status=PaymentStatus.COMPLETED
        )
        
        with pytest.raises(ValueError, match="Можно завершить только платеж в статусе 'pending'"):
            payment.mark_completed()

    def test_mark_failed_success(self, test_user, test_account):
        """Тест отметки платежа как неудачного"""
        payment = Payment(
            transaction_id="test-fail",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=100.00,
            status=PaymentStatus.PENDING
        )
        
        payment.mark_failed("Тестовая ошибка")
        assert payment.status == PaymentStatus.FAILED
        assert payment.description == "Ошибка: Тестовая ошибка"

    def test_mark_failed_without_reason(self, test_user, test_account):
        """Тест отметки платежа как неудачного без причины"""
        payment = Payment(
            transaction_id="test-fail-no-reason",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=100.00,
            status=PaymentStatus.PENDING
        )
        
        payment.mark_failed()
        assert payment.status == PaymentStatus.FAILED
        assert payment.description is None

    def test_cancel_payment_success(self, test_user, test_account):
        """Тест отмены платежа"""
        payment = Payment(
            transaction_id="test-cancel",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=100.00,
            status=PaymentStatus.PENDING
        )
        
        payment.cancel("Отменен пользователем")
        assert payment.status == PaymentStatus.CANCELLED
        assert payment.description == "Отменен: Отменен пользователем"

    def test_cancel_failed_payment(self, test_user, test_account):
        """Тест отмены неудачного платежа"""
        payment = Payment(
            transaction_id="test-cancel-failed",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=100.00,
            status=PaymentStatus.FAILED
        )
        
        payment.cancel()
        assert payment.status == PaymentStatus.CANCELLED

    def test_cancel_invalid_status(self, test_user, test_account):
        """Тест отмены платежа с неверным статусом"""
        payment = Payment(
            transaction_id="test-cancel-invalid",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=100.00,
            status=PaymentStatus.COMPLETED
        )
        
        with pytest.raises(ValueError, match="Можно отменить только платеж в статусе 'pending' или 'failed'"):
            payment.cancel()

    def test_create_deposit(self, test_user, test_account):
        """Тест создания платежа пополнения"""
        payment = Payment.create_deposit(
            transaction_id="deposit-123",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=500.00,
            currency="USD",
            description="Тестовое пополнение",
            external_data='{"method": "card"}'
        )
        
        assert payment.transaction_id == "deposit-123"
        assert payment.account_id == test_account.id
        assert payment.user_id == test_user.id
        assert payment.amount == Decimal('500.00')
        assert payment.currency == "USD"
        assert payment.payment_type == PaymentType.DEPOSIT
        assert payment.status == PaymentStatus.PENDING
        assert payment.description == "Тестовое пополнение"
        assert payment.external_data == '{"method": "card"}'

    def test_create_deposit_invalid_amount(self, test_user, test_account):
        """Тест создания пополнения с неверной суммой"""
        with pytest.raises(ValueError, match="Сумма пополнения должна быть положительной"):
            Payment.create_deposit(
                transaction_id="deposit-invalid",
                account_id=test_account.id,
                user_id=test_user.id,
                amount=-100.00
            )

    def test_create_withdrawal(self, test_user, test_account):
        """Тест создания платежа списания"""
        payment = Payment.create_withdrawal(
            transaction_id="withdrawal-123",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=200.00,
            currency="EUR",
            description="Тестовое списание"
        )
        
        assert payment.transaction_id == "withdrawal-123"
        assert payment.payment_type == PaymentType.WITHDRAWAL
        assert payment.description == "Тестовое списание"

    def test_create_transfer(self, test_user, test_account, test_account2):
        """Тест создания платежа перевода"""
        payment = Payment.create_transfer(
            transaction_id="transfer-123",
            from_account_id=test_account.id,
            to_account_id=test_account2.id,
            user_id=test_user.id,
            amount=300.00,
            description="Тестовый перевод"
        )
        
        assert payment.transaction_id == "transfer-123"
        assert payment.account_id == test_account.id
        assert payment.target_account_id == test_account2.id
        assert payment.payment_type == PaymentType.TRANSFER
        assert payment.description == "Тестовый перевод"

    def test_create_transfer_same_account(self, test_user, test_account):
        """Тест создания перевода на тот же счет"""
        with pytest.raises(ValueError, match="Нельзя переводить на тот же счет"):
            Payment.create_transfer(
                transaction_id="transfer-invalid",
                from_account_id=test_account.id,
                to_account_id=test_account.id,
                user_id=test_user.id,
                amount=100.00
            )

    def test_create_with_validation_success(self, test_user, test_account):
        """Тест создания платежа с валидацией"""
        payment = Payment.create_with_validation(
            transaction_id="validated-123",
            account_id=test_account.id,
            account_user_id=test_user.id,
            amount=150.00,
            description="Валидированный платеж"
        )
        
        assert payment.user_id == test_user.id
        assert payment.account_id == test_account.id

    def test_create_with_validation_inconsistent(self, test_user, test_account):
        """Тест создания платежа с несогласованными данными"""
        payment = Payment(
            transaction_id="validated-invalid",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=150.00
        )
        
        different_user_id = 999
        with pytest.raises(ValueError, match="не соответствует"):
            payment.validate_account_user_consistency(different_user_id)

    def test_validate_account_user_consistency_success(self, test_user, test_account):
        """Тест успешной валидации согласованности"""
        payment = Payment(
            transaction_id="validation-test",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=100.00
        )
        
        payment.validate_account_user_consistency(test_user.id)

    def test_validate_account_user_consistency_failure(self, test_user, test_account):
        """Тест неудачной валидации согласованности"""
        payment = Payment(
            transaction_id="validation-fail-test",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=100.00
        )
        
        different_user_id = 999
        with pytest.raises(ValueError, match="не соответствует"):
            payment.validate_account_user_consistency(different_user_id)

    def test_get_webhook_data(self, test_user, test_account):
        """Тест получения данных в формате веб-хука"""
        payment = Payment(
            transaction_id="webhook-test",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=75.50
        )
        
        webhook_data = payment.get_webhook_data()
        
        assert webhook_data == {
            "transaction_id": "webhook-test",
            "user_id": test_user.id,
            "account_id": test_account.id,
            "amount": 75.50
        }

    async def test_payment_database_operations(self, test_session, test_user, test_account):
        """Тест операций с Payment в базе данных"""
        payment = Payment(
            transaction_id="db-test-123",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=450.75,
            currency="USD",
            description="Database test payment"
        )
        
        test_session.add(payment)
        await test_session.commit()
        await test_session.refresh(payment)
        
        assert payment.id is not None
        assert isinstance(payment.id, int)
        assert payment.created_at is not None
        assert payment.updated_at is not None

    async def test_payment_unique_transaction_id(self, test_session, test_user, test_account):
        """Тест уникальности transaction_id"""
        payment1 = Payment(
            transaction_id="unique-test-456",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=100.00
        )
        payment2 = Payment(
            transaction_id="unique-test-456",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=200.00
        )
        
        test_session.add(payment1)
        await test_session.commit()
        
        test_session.add(payment2)
        
        with pytest.raises(Exception):
            await test_session.commit()

    async def test_payment_relationships(self, test_session, test_user, test_account):
        """Тест связей Payment с другими моделями"""
        payment = Payment(
            transaction_id="relationship-test",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=350.00
        )
        
        test_session.add(payment)
        await test_session.commit()
        await test_session.refresh(payment)
        
        assert payment.account is not None
        assert payment.account.id == test_account.id
        assert payment.user is not None
        assert payment.user.id == test_user.id

    async def test_payment_update_status(self, test_session, test_user, test_account):
        """Тест обновления статуса платежа"""
        payment = Payment(
            transaction_id="status-update-test",
            account_id=test_account.id,
            user_id=test_user.id,
            amount=125.00,
            status=PaymentStatus.PENDING
        )
        
        test_session.add(payment)
        await test_session.commit()
        await test_session.refresh(payment)
        
        payment.mark_completed()
        await test_session.commit()
        await test_session.refresh(payment)
        
        assert payment.status == PaymentStatus.COMPLETED

    async def test_multiple_payments_for_account(self, test_session, test_user, test_account):
        """Тест создания нескольких платежей для одного счета"""
        payments = [
            Payment(transaction_id="multi-1", account_id=test_account.id, user_id=test_user.id, amount=100.00),
            Payment(transaction_id="multi-2", account_id=test_account.id, user_id=test_user.id, amount=200.00),
            Payment(transaction_id="multi-3", account_id=test_account.id, user_id=test_user.id, amount=300.00),
        ]
        
        test_session.add_all(payments)
        await test_session.commit()
        
        from sqlalchemy import select
        result = await test_session.execute(
            select(Payment).where(Payment.account_id == test_account.id)
        )
        account_payments = result.scalars().all()
        
        assert len(account_payments) == 3
        
        amounts = [float(p.amount) for p in account_payments]
        assert 100.00 in amounts
        assert 200.00 in amounts
        assert 300.00 in amounts

    def test_payment_status_enum_values(self):
        """Тест значений enum PaymentStatus"""
        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.COMPLETED.value == "completed"
        assert PaymentStatus.FAILED.value == "failed"
        assert PaymentStatus.CANCELLED.value == "cancelled"

    def test_payment_type_enum_values(self):
        """Тест значений enum PaymentType"""
        assert PaymentType.DEPOSIT.value == "deposit"
        assert PaymentType.WITHDRAWAL.value == "withdrawal"
        assert PaymentType.TRANSFER.value == "transfer"
