"""Тесты для схем пользовательских операций"""

import pytest
from decimal import Decimal
from datetime import datetime
from pydantic import ValidationError

from app.schemas.users import (
    AccountResponse,
    PaymentResponse,
    UserAccountsResponse,
    UserPaymentsResponse
)


class TestAccountResponse:
    """Тесты для схемы AccountResponse"""
    
    def test_account_response_valid(self):
        """Тест валидного ответа с данными счета"""
        data = {
            "id": 1,
            "balance": "1250.50",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-20T15:45:00Z"
        }
        
        account = AccountResponse(**data)
        
        assert account.id == 1
        assert account.balance == Decimal("1250.50")
        assert account.created_at == datetime.fromisoformat("2024-01-15T10:30:00+00:00")
        assert account.updated_at == datetime.fromisoformat("2024-01-20T15:45:00+00:00")
    
    def test_account_response_without_updated_at(self):
        """Тест валидного ответа без updated_at"""
        data = {
            "id": 1,
            "balance": "1250.50",
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        account = AccountResponse(**data)
        
        assert account.id == 1
        assert account.balance == Decimal("1250.50")
        assert account.created_at == datetime.fromisoformat("2024-01-15T10:30:00+00:00")
        assert account.updated_at is None
    
    def test_account_response_decimal_balance(self):
        """Тест различных форматов баланса"""
        test_cases = [
            ("0", Decimal("0")),
            ("0.00", Decimal("0.00")),
            ("1000", Decimal("1000")),
            ("999.99", Decimal("999.99")),
            ("1000000.01", Decimal("1000000.01")),
        ]
        
        for balance_str, expected_decimal in test_cases:
            data = {
                "id": 1,
                "balance": balance_str,
                "created_at": "2024-01-15T10:30:00Z"
            }
            
            account = AccountResponse(**data)
            assert account.balance == expected_decimal
    
    def test_account_response_invalid_id(self):
        """Тест невалидного ID"""
        data = {
            "id": "not_a_number",
            "balance": "1250.50",
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AccountResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "int_parsing" for error in errors)
    
    def test_account_response_invalid_balance(self):
        """Тест невалидного баланса"""
        data = {
            "id": 1,
            "balance": "not_a_number",
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AccountResponse(**data)
        
        errors = exc_info.value.errors()
        assert any("decimal" in error["type"] for error in errors)
    
    def test_account_response_invalid_created_at(self):
        """Тест невалидной даты создания"""
        data = {
            "id": 1,
            "balance": "1250.50",
            "created_at": "invalid-date"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AccountResponse(**data)
        
        errors = exc_info.value.errors()
        assert any("datetime" in error["type"] for error in errors)
    
    def test_account_response_missing_required_fields(self):
        """Тест отсутствующих обязательных полей"""
        # Тест отсутствующего ID
        data = {
            "balance": "1250.50",
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AccountResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" for error in errors)
        
        # Тест отсутствующего баланса
        data = {
            "id": 1,
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AccountResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" for error in errors)


class TestPaymentResponse:
    """Тесты для схемы PaymentResponse"""
    
    def test_payment_response_valid(self):
        """Тест валидного ответа с данными платежа"""
        data = {
            "id": 1,
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "amount": "100.00",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:31:00Z"
        }
        
        payment = PaymentResponse(**data)
        
        assert payment.id == 1
        assert payment.transaction_id == "5eae174f-7cd0-472c-bd36-35660f00132b"
        assert payment.amount == Decimal("100.00")
        assert payment.created_at == datetime.fromisoformat("2024-01-15T10:30:00+00:00")
        assert payment.updated_at == datetime.fromisoformat("2024-01-15T10:31:00+00:00")
    
    def test_payment_response_without_updated_at(self):
        """Тест валидного ответа без updated_at"""
        data = {
            "id": 1,
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "amount": "100.00",
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        payment = PaymentResponse(**data)
        
        assert payment.id == 1
        assert payment.transaction_id == "5eae174f-7cd0-472c-bd36-35660f00132b"
        assert payment.amount == Decimal("100.00")
        assert payment.created_at == datetime.fromisoformat("2024-01-15T10:30:00+00:00")
        assert payment.updated_at is None
    
    def test_payment_response_various_transaction_ids(self):
        """Тест различных форматов transaction_id"""
        test_cases = [
            "5eae174f-7cd0-472c-bd36-35660f00132b",  # UUID
            "tx_12345",  # строка с префиксом
            "1234567890",  # числовая строка
            "custom-transaction-id-2024",  # кастомный формат
        ]
        
        for transaction_id in test_cases:
            data = {
                "id": 1,
                "transaction_id": transaction_id,
                "amount": "100.00",
                "created_at": "2024-01-15T10:30:00Z"
            }
            
            payment = PaymentResponse(**data)
            assert payment.transaction_id == transaction_id
    
    def test_payment_response_various_amounts(self):
        """Тест различных сумм платежей"""
        test_cases = [
            ("0.01", Decimal("0.01")),
            ("1.00", Decimal("1.00")),
            ("999.99", Decimal("999.99")),
            ("1000000", Decimal("1000000")),
            ("1500.50", Decimal("1500.50")),
        ]
        
        for amount_str, expected_decimal in test_cases:
            data = {
                "id": 1,
                "transaction_id": "tx123",
                "amount": amount_str,
                "created_at": "2024-01-15T10:30:00Z"
            }
            
            payment = PaymentResponse(**data)
            assert payment.amount == expected_decimal
    
    def test_payment_response_invalid_id(self):
        """Тест невалидного ID"""
        data = {
            "id": "not_a_number",
            "transaction_id": "tx123",
            "amount": "100.00",
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PaymentResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "int_parsing" for error in errors)
    
    def test_payment_response_empty_transaction_id(self):
        """Тест пустого transaction_id"""
        data = {
            "id": 1,
            "transaction_id": "",
            "amount": "100.00",
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        # Пустая строка должна быть валидной, так как в схеме нет ограничений
        payment = PaymentResponse(**data)
        assert payment.transaction_id == ""
    
    def test_payment_response_invalid_amount(self):
        """Тест невалидной суммы"""
        data = {
            "id": 1,
            "transaction_id": "tx123",
            "amount": "not_a_number",
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PaymentResponse(**data)
        
        errors = exc_info.value.errors()
        assert any("decimal" in error["type"] for error in errors)
    
    def test_payment_response_missing_required_fields(self):
        """Тест отсутствующих обязательных полей"""
        # Тест отсутствующего transaction_id
        data = {
            "id": 1,
            "amount": "100.00",
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PaymentResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" for error in errors)


class TestUserAccountsResponse:
    """Тесты для схемы UserAccountsResponse"""
    
    def test_user_accounts_response_valid(self):
        """Тест валидного ответа со списком счетов"""
        data = {
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
        
        response = UserAccountsResponse(**data)
        
        assert len(response.accounts) == 2
        assert response.accounts[0].id == 1
        assert response.accounts[0].balance == Decimal("1250.50")
        assert response.accounts[1].id == 2
        assert response.accounts[1].balance == Decimal("750.25")
    
    def test_user_accounts_response_empty_list(self):
        """Тест ответа с пустым списком счетов"""
        data = {
            "accounts": []
        }
        
        response = UserAccountsResponse(**data)
        
        assert len(response.accounts) == 0
        assert response.accounts == []
    
    def test_user_accounts_response_single_account(self):
        """Тест ответа с одним счетом"""
        data = {
            "accounts": [
                {
                    "id": 1,
                    "balance": "1000.00",
                    "created_at": "2024-01-15T10:30:00Z"
                }
            ]
        }
        
        response = UserAccountsResponse(**data)
        
        assert len(response.accounts) == 1
        assert response.accounts[0].id == 1
        assert response.accounts[0].balance == Decimal("1000.00")
        assert response.accounts[0].updated_at is None
    
    def test_user_accounts_response_invalid_account(self):
        """Тест невалидного счета в списке"""
        data = {
            "accounts": [
                {
                    "id": "invalid",  # невалидный ID
                    "balance": "1000.00",
                    "created_at": "2024-01-15T10:30:00Z"
                }
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserAccountsResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "int_parsing" for error in errors)
    
    def test_user_accounts_response_missing_accounts(self):
        """Тест отсутствующего поля accounts"""
        data = {}
        
        with pytest.raises(ValidationError) as exc_info:
            UserAccountsResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" for error in errors)


class TestUserPaymentsResponse:
    """Тесты для схемы UserPaymentsResponse"""
    
    def test_user_payments_response_valid(self):
        """Тест валидного ответа со списком платежей"""
        data = {
            "payments": [
                {
                    "id": 1,
                    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
                    "amount": "100.00",
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:31:00Z"
                },
                {
                    "id": 2,
                    "transaction_id": "6fae184g-8cd1-572d-be47-46771g00243c",
                    "amount": "250.50",
                    "created_at": "2024-01-20T14:15:00Z"
                }
            ]
        }
        
        response = UserPaymentsResponse(**data)
        
        assert len(response.payments) == 2
        assert response.payments[0].id == 1
        assert response.payments[0].amount == Decimal("100.00")
        assert response.payments[1].id == 2
        assert response.payments[1].amount == Decimal("250.50")
        assert response.payments[1].updated_at is None
    
    def test_user_payments_response_empty_list(self):
        """Тест ответа с пустым списком платежей"""
        data = {
            "payments": []
        }
        
        response = UserPaymentsResponse(**data)
        
        assert len(response.payments) == 0
        assert response.payments == []
    
    def test_user_payments_response_single_payment(self):
        """Тест ответа с одним платежом"""
        data = {
            "payments": [
                {
                    "id": 1,
                    "transaction_id": "tx_12345",
                    "amount": "500.00",
                    "created_at": "2024-01-15T10:30:00Z"
                }
            ]
        }
        
        response = UserPaymentsResponse(**data)
        
        assert len(response.payments) == 1
        assert response.payments[0].id == 1
        assert response.payments[0].transaction_id == "tx_12345"
        assert response.payments[0].amount == Decimal("500.00")
    
    def test_user_payments_response_invalid_payment(self):
        """Тест невалидного платежа в списке"""
        data = {
            "payments": [
                {
                    "id": 1,
                    "transaction_id": "tx123",
                    "amount": "not_a_number",  # невалидная сумма
                    "created_at": "2024-01-15T10:30:00Z"
                }
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserPaymentsResponse(**data)
        
        errors = exc_info.value.errors()
        assert any("decimal" in error["type"] for error in errors)
    
    def test_user_payments_response_missing_payments(self):
        """Тест отсутствующего поля payments"""
        data = {}
        
        with pytest.raises(ValidationError) as exc_info:
            UserPaymentsResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" for error in errors)


class TestSchemasIntegration:
    """Интеграционные тесты схем пользователей"""
    
    def test_schemas_json_serialization(self):
        """Тест сериализации схем в JSON"""
        account = AccountResponse(
            id=1,
            balance=Decimal("1000.50"),
            created_at=datetime.fromisoformat("2024-01-15T10:30:00+00:00")
        )
        
        json_data = account.model_dump_json()
        assert '"id":1' in json_data
        assert '"balance":"1000.50"' in json_data
        assert "2024-01-15T10:30:00" in json_data
    
    def test_schemas_dict_conversion(self):
        """Тест конвертации схем в словари"""
        payment = PaymentResponse(
            id=1,
            transaction_id="tx123",
            amount=Decimal("100.00"),
            created_at=datetime.fromisoformat("2024-01-15T10:30:00+00:00")
        )
        
        payment_dict = payment.model_dump()
        
        assert payment_dict["id"] == 1
        assert payment_dict["transaction_id"] == "tx123"
        assert payment_dict["amount"] == Decimal("100.00")
        assert payment_dict["updated_at"] is None
    
    def test_nested_schemas_validation(self):
        """Тест валидации вложенных схем"""
        # Создаем UserAccountsResponse с множественными счетами
        accounts_data = {
            "accounts": [
                {
                    "id": i,
                    "balance": f"{i * 100}.00",
                    "created_at": "2024-01-15T10:30:00Z"
                }
                for i in range(1, 6)  # 5 счетов
            ]
        }
        
        response = UserAccountsResponse(**accounts_data)
        
        assert len(response.accounts) == 5
        for i, account in enumerate(response.accounts, 1):
            assert account.id == i
            assert account.balance == Decimal(f"{i * 100}.00")
    
    def test_decimal_precision(self):
        """Тест точности работы с Decimal"""
        # Тестируем что Decimal сохраняет точность
        test_amounts = [
            "0.01",
            "0.001",
            "999.999",
            "1000000.0001"
        ]
        
        for amount_str in test_amounts:
            account = AccountResponse(
                id=1,
                balance=amount_str,
                created_at=datetime.fromisoformat("2024-01-15T10:30:00+00:00")
            )
            
            # Проверяем что точность сохранена
            assert str(account.balance) == amount_str
    
    def test_datetime_timezone_handling(self):
        """Тест обработки временных зон в datetime"""
        # Тест с различными форматами даты
        datetime_formats = [
            "2024-01-15T10:30:00Z",  # UTC с Z
            "2024-01-15T10:30:00+00:00",  # UTC с +00:00
            "2024-01-15T10:30:00+03:00",  # MSK
            "2024-01-15T10:30:00-05:00",  # EST
        ]
        
        for dt_str in datetime_formats:
            account = AccountResponse(
                id=1,
                balance="1000.00",
                created_at=dt_str
            )
            
            # Проверяем что дата парсится корректно
            assert account.created_at is not None
            assert isinstance(account.created_at, datetime)
