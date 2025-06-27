"""Роуты для пользователей"""

from datetime import datetime
from sanic import Blueprint
from sanic.response import json as sanic_json
from sanic.request import Request

from app.schemas.auth import UserResponse
from app.schemas.users import UserAccountsResponse, UserPaymentsResponse
from app.auth.service import user_required
from app.services import UserService, AccountService, PaymentService

user_bp = Blueprint("user", url_prefix="/api/v1/user")


@user_bp.get("/me")
@user_required
async def get_user_profile(request: Request):
    """Получить данные о себе (id, email, full_name)"""
    try:
        # Получаем текущего пользователя из токена
        current_user = request.ctx.current_user
        
        response = UserResponse(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            created_at=current_user.created_at or datetime.now(),
            updated_at=current_user.updated_at
        )
        
        return sanic_json(response.model_dump())
        
    except Exception as e:
        return sanic_json(
            {"error": str(e)}, 
            status=400
        )


@user_bp.get("/accounts")
@user_required
async def get_user_accounts(request: Request):
    """Получить список своих счетов и балансов"""
    try:
        # Получаем текущего пользователя из токена
        current_user = request.ctx.current_user
        
        # Получаем счета пользователя из базы данных
        accounts = await AccountService.get_user_accounts(current_user.id)
        
        accounts_data = {
            "accounts": [
                {
                    "id": account.id,
                    "balance": str(account.balance),
                    "created_at": account.created_at.isoformat() if account.created_at else None,
                    "updated_at": account.updated_at.isoformat() if account.updated_at else None
                }
                for account in accounts
            ]
        }
        
        response = UserAccountsResponse(**accounts_data)
        return sanic_json(response.model_dump())
        
    except Exception as e:
        return sanic_json(
            {"error": str(e)}, 
            status=400
        )


@user_bp.get("/payments")
@user_required
async def get_user_payments(request: Request):
    """Получить список своих платежей"""
    try:
        # Получаем текущего пользователя из токена
        current_user = request.ctx.current_user
        
        # Получаем платежи пользователя из базы данных
        payments = await PaymentService.get_user_payments(current_user.id)
        
        payments_data = {
            "payments": [
                {
                    "id": payment.id,
                    "transaction_id": payment.transaction_id,
                    "amount": str(payment.amount),
                    "created_at": payment.created_at.isoformat() if payment.created_at else None,
                    "updated_at": payment.updated_at.isoformat() if payment.updated_at else None
                }
                for payment in payments
            ]
        }
        
        response = UserPaymentsResponse(**payments_data)
        return sanic_json(response.model_dump())
        
    except Exception as e:
        return sanic_json(
            {"error": str(e)}, 
            status=400
        )
