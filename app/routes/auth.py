"""Роуты для авторизации"""

from datetime import datetime
from sanic import Blueprint
from sanic.response import json as sanic_json
from sanic.request import Request

from app.schemas.auth import LoginRequest, LoginResponse, UserResponse, TokenResponse
from app.auth.service import AuthService

auth_bp = Blueprint("auth", url_prefix="/api/v1/auth")


@auth_bp.post("/login")
async def login(request: Request):
    """Авторизация пользователя по email/password"""
    try:
        # Валидация входных данных
        login_data = LoginRequest(**request.json)
        
        # Аутентификация пользователя
        user_data = await AuthService.authenticate_user(login_data.email, login_data.password)
        
        if not user_data:
            return sanic_json(
                {"error": "Неверный email или пароль"}, 
                status=401
            )
        
        # Создаем ответ с данными пользователя
        user_response = UserResponse(
            id=user_data.id,
            email=user_data.email,
            full_name=user_data.full_name,
            created_at=user_data.created_at or datetime.now(),
            updated_at=user_data.updated_at
        )
        
        token_response = TokenResponse(
            access_token="temp_token",  # TODO: генерировать реальный токен
            token_type="bearer",
            expires_in=3600
        )
        
        response = LoginResponse(
            user=user_response,
            token=token_response
        )
        
        return sanic_json(response.model_dump())
        
    except Exception as e:
        return sanic_json(
            {"error": str(e)}, 
            status=400
        )


@auth_bp.post("/admin/login")
async def admin_login(request: Request):
    """Авторизация администратора по email/password"""
    try:
        # Валидация входных данных
        login_data = LoginRequest(**request.json)
        
        # Аутентификация администратора
        admin_data = await AuthService.authenticate_admin(login_data.email, login_data.password)
        
        if not admin_data:
            return sanic_json(
                {"error": "Неверный email или пароль"}, 
                status=401
            )
        
        # Создаем ответ с данными администратора
        user_response = UserResponse(
            id=admin_data.id,
            email=admin_data.email,
            full_name=admin_data.full_name,
            created_at=admin_data.created_at or datetime.now(),
            updated_at=admin_data.updated_at
        )
        
        token_response = TokenResponse(
            access_token="temp_token",  # TODO: генерировать реальный токен
            token_type="bearer",
            expires_in=3600
        )
        
        response = LoginResponse(
            user=user_response,
            token=token_response
        )
        
        return sanic_json(response.model_dump())
        
    except Exception as e:
        return sanic_json(
            {"error": str(e)}, 
            status=400
        )
