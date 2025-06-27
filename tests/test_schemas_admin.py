"""Тесты для схем административных операций"""

import pytest
from decimal import Decimal
from datetime import datetime
from pydantic import ValidationError

from app.schemas.admin import (
    AdminUserResponse,
    AdminAccountResponse,
    UserManagementRequest,
    AdminUsersListResponse,
    AdminAccountsListResponse,
    AdminOperationResponse
)


class TestAdminUserResponse:
    """Тесты для схемы AdminUserResponse"""
    
    def test_admin_user_response_valid(self):
        """Тест валидного ответа с данными пользователя для админки"""
        data = {
            "id": 1,
            "email": "user@example.com",
            "full_name": "Иван Иванов",
            "created_at": "2024-01-10T08:00:00Z",
            "updated_at": "2024-01-15T12:30:00Z"
        }
        
        user = AdminUserResponse(**data)
        
        assert user.id == 1
        assert user.email == "user@example.com"
        assert user.full_name == "Иван Иванов"
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_admin_user_response_without_optional_fields(self):
        """Тест ответа без необязательных полей"""
        data = {
            "id": 1,
            "email": "user@example.com",
            "full_name": "Иван Иванов",
            "created_at": "2024-01-10T08:00:00Z"
        }
        
        user = AdminUserResponse(**data)
        
        assert user.id == 1
        assert user.email == "user@example.com"
        assert user.full_name == "Иван Иванов"
        assert user.updated_at is None


class TestAdminAccountResponse:
    """Тесты для схемы AdminAccountResponse"""
    
    def test_admin_account_response_valid(self):
        """Тест валидного ответа с данными счета для админки"""
        data = {
            "id": 1,
            "balance": "1250.50",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-20T15:45:00Z"
        }
        
        account = AdminAccountResponse(**data)
        
        assert account.id == 1
        assert account.balance == Decimal("1250.50")
        assert account.created_at is not None
        assert account.updated_at is not None


class TestUserManagementRequest:
    """Тесты для схемы UserManagementRequest"""
    
    def test_user_management_request_create(self):
        """Тест создания пользователя"""
        data = {
            "action": "create",
            "email": "newuser@example.com",
            "full_name": "Новый Пользователь",
            "password": "password123"
        }
        
        request = UserManagementRequest(**data)
        
        assert request.action == "create"
        assert request.email == "newuser@example.com"
        assert request.full_name == "Новый Пользователь"
        assert request.password == "password123"


class TestAdminOperationResponse:
    """Тесты для схемы AdminOperationResponse"""
    
    def test_admin_operation_response_success(self):
        """Тест успешной операции"""
        data = {
            "success": True,
            "message": "Операция выполнена успешно",
            "details": "Пользователь создан"
        }
        
        response = AdminOperationResponse(**data)
        
        assert response.success is True
        assert response.message == "Операция выполнена успешно"
        assert response.details == "Пользователь создан"
