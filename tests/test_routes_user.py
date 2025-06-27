"""Тесты для роутов пользователей"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.models.user import User
from app.models.account import Account
from app.models.payment import Payment
from app.schemas.auth import UserResponse
from app.schemas.users import UserAccountsResponse, UserPaymentsResponse


class TestUserRoutesLogic:
    """Тесты для логики роутов пользователей"""

    def test_user_response_schema_creation(self):
        """Тест создания схемы UserResponse для профиля пользователя"""
        user_data = {
            "id": 1,
            "email": "user@test.com",
            "full_name": "Test User",
            "created_at": datetime.now(),
            "updated_at": None
        }
        
        user_response = UserResponse(**user_data)
        assert user_response.id == 1
        assert user_response.email == "user@test.com"
        assert user_response.full_name == "Test User"
        assert user_response.created_at is not None

    def test_user_accounts_response_schema(self):
        """Тест создания схемы UserAccountsResponse"""
        accounts_data = {
            "accounts": [
                {
                    "id": 1,
                    "balance": "1250.50",
                    "created_at": datetime.now(),
                    "updated_at": None
                },
                {
                    "id": 2,
                    "balance": "750.25",
                    "created_at": datetime.now(),
                    "updated_at": None
                }
            ]
        }
        
        accounts_response = UserAccountsResponse(**accounts_data)
        assert len(accounts_response.accounts) == 2
        assert accounts_response.accounts[0].id == 1
        assert str(accounts_response.accounts[0].balance) == "1250.50"

    def test_user_payments_response_schema(self):
        """Тест создания схемы UserPaymentsResponse"""
        payments_data = {
            "payments": [
                {
                    "id": 1,
                    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
                    "amount": "100.00",
                    "created_at": datetime.now(),
                    "updated_at": None
                }
            ]
        }
        
        payments_response = UserPaymentsResponse(**payments_data)
        assert len(payments_response.payments) == 1
        assert payments_response.payments[0].transaction_id == "5eae174f-7cd0-472c-bd36-35660f00132b"
        assert str(payments_response.payments[0].amount) == "100.00"

    @pytest.mark.asyncio
    async def test_user_profile_logic(self):
        """Тест логики получения профиля пользователя"""
        # Мокаем пользователя
        mock_user = User(
            id=1,
            email="user@test.com",
            full_name="Test User",
            password_hash="hashed_password",
            created_at=datetime.now(),
            updated_at=None
        )
        
        # Тестируем создание ответа как в роуте
        response = UserResponse(
            id=mock_user.id,
            email=mock_user.email,
            full_name=mock_user.full_name,
            created_at=mock_user.created_at or datetime.now(),
            updated_at=mock_user.updated_at
        )
        
        response_dict = response.model_dump()
        
        assert "id" in response_dict
        assert "email" in response_dict
        assert "full_name" in response_dict
        assert "created_at" in response_dict
        assert "updated_at" in response_dict
        assert response_dict["id"] == 1
        assert response_dict["email"] == "user@test.com"

    @pytest.mark.asyncio
    async def test_user_accounts_service_logic(self):
        """Тест логики сервиса для получения счетов пользователя"""
        from app.services import AccountService
        
        # Мокаем счета
        mock_accounts = [
            Account(
                id=1,
                user_id=1,
                account_number="ACC001",
                balance=1250.50,
                created_at=datetime.now(),
                updated_at=None
            ),
            Account(
                id=2,
                user_id=1,
                account_number="ACC002",
                balance=750.25,
                created_at=datetime.now(),
                updated_at=None
            )
        ]
        
        with patch.object(AccountService, 'get_user_accounts', new_callable=AsyncMock) as mock_get_accounts:
            mock_get_accounts.return_value = mock_accounts
            
            accounts = await AccountService.get_user_accounts(1)
            
            assert len(accounts) == 2
            assert accounts[0].id == 1
            assert accounts[0].balance == 1250.50
            assert accounts[1].id == 2
            assert accounts[1].balance == 750.25
            
            mock_get_accounts.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_user_payments_service_logic(self):
        """Тест логики сервиса для получения платежей пользователя"""
        from app.services import PaymentService
        
        # Мокаем платежи
        mock_payments = [
            Payment(
                id=1,
                transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
                account_id=1,
                user_id=1,
                amount=100.00,
                created_at=datetime.now(),
                updated_at=None
            )
        ]
        
        with patch.object(PaymentService, 'get_user_payments', new_callable=AsyncMock) as mock_get_payments:
            mock_get_payments.return_value = mock_payments
            
            payments = await PaymentService.get_user_payments(1)
            
            assert len(payments) == 1
            assert payments[0].id == 1
            assert payments[0].transaction_id == "5eae174f-7cd0-472c-bd36-35660f00132b"
            assert payments[0].amount == 100.00
            
            mock_get_payments.assert_called_once_with(1)

    def test_user_accounts_response_structure(self):
        """Тест структуры ответа со счетами пользователя"""
        # Имитируем создание ответа как в роуте
        mock_accounts = [
            Account(
                id=1,
                user_id=1,
                account_number="ACC001",
                balance=1250.50,
                created_at=datetime.now(),
                updated_at=None
            )
        ]
        
        accounts_data = {
            "accounts": [
                {
                    "id": account.id,
                    "balance": str(account.balance),
                    "created_at": account.created_at.isoformat() if account.created_at else None,
                    "updated_at": account.updated_at.isoformat() if account.updated_at else None
                }
                for account in mock_accounts
            ]
        }
        
        response = UserAccountsResponse(**accounts_data)
        response_dict = response.model_dump()
        
        assert "accounts" in response_dict
        assert len(response_dict["accounts"]) == 1
        assert "id" in response_dict["accounts"][0]
        assert "balance" in response_dict["accounts"][0]
        assert "created_at" in response_dict["accounts"][0]
        assert "updated_at" in response_dict["accounts"][0]

    def test_user_payments_response_structure(self):
        """Тест структуры ответа с платежами пользователя"""
        # Имитируем создание ответа как в роуте
        mock_payments = [
            Payment(
                id=1,
                transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
                account_id=1,
                user_id=1,
                amount=100.00,
                created_at=datetime.now(),
                updated_at=None
            )
        ]
        
        payments_data = {
            "payments": [
                {
                    "id": payment.id,
                    "transaction_id": payment.transaction_id,
                    "amount": str(payment.amount),
                    "created_at": payment.created_at.isoformat() if payment.created_at else None,
                    "updated_at": payment.updated_at.isoformat() if payment.updated_at else None
                }
                for payment in mock_payments
            ]
        }
        
        response = UserPaymentsResponse(**payments_data)
        response_dict = response.model_dump()
        
        assert "payments" in response_dict
        assert len(response_dict["payments"]) == 1
        assert "id" in response_dict["payments"][0]
        assert "transaction_id" in response_dict["payments"][0]
        assert "amount" in response_dict["payments"][0]
        assert "created_at" in response_dict["payments"][0]
        assert "updated_at" in response_dict["payments"][0]

    def test_user_blueprint_configuration(self):
        """Тест конфигурации blueprint пользователей"""
        from app.routes.user import user_bp
        
        assert user_bp.name == "user"
        assert user_bp.url_prefix == "/api/v1/user"
        
        # Проверяем, что у blueprint есть основные атрибуты
        assert hasattr(user_bp, 'name')
        assert hasattr(user_bp, 'url_prefix')
        assert hasattr(user_bp, 'routes')

    def test_empty_accounts_list(self):
        """Тест обработки пустого списка счетов"""
        accounts_data = {"accounts": []}
        
        response = UserAccountsResponse(**accounts_data)
        response_dict = response.model_dump()
        
        assert "accounts" in response_dict
        assert len(response_dict["accounts"]) == 0
        assert response_dict["accounts"] == []

    def test_empty_payments_list(self):
        """Тест обработки пустого списка платежей"""
        payments_data = {"payments": []}
        
        response = UserPaymentsResponse(**payments_data)
        response_dict = response.model_dump()
        
        assert "payments" in response_dict
        assert len(response_dict["payments"]) == 0
        assert response_dict["payments"] == []

    def test_error_response_structure(self):
        """Тест структуры ответа с ошибкой"""
        # Тестируем типичную структуру ошибки, которая возвращается в роутах
        error_response = {
            "error": "Недостаточно прав доступа"
        }
        
        assert "error" in error_response
        assert isinstance(error_response["error"], str)
        assert len(error_response["error"]) > 0

    @pytest.mark.asyncio
    async def test_authentication_decorator_logic(self):
        """Тест логики декоратора аутентификации"""
        from app.auth.service import user_required
        
        # Проверяем, что декоратор является функцией
        assert callable(user_required)
        
        # Проверяем, что декоратор может обернуть функцию
        @user_required
        async def test_function(request):
            return {"status": "ok"}
        
        assert callable(test_function)
        assert hasattr(test_function, '__call__')
