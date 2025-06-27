"""Роуты для администраторов"""

from datetime import datetime
from sanic import Blueprint
from sanic.response import json as sanic_json
from sanic.request import Request

from app.schemas.auth import UserResponse
from app.auth.service import admin_required
from app.services import UserService, AccountService

admin_bp = Blueprint("admin", url_prefix="/api/v1/admin")


@admin_bp.get("/me")
@admin_required
async def get_admin_profile(request: Request):
    """Получить данные о себе (id, email, full_name)"""
    try:
        # Получаем текущего администратора из токена
        current_admin = request.ctx.current_user
        
        response = UserResponse(
            id=current_admin.id,
            email=current_admin.email,
            full_name=current_admin.full_name,
            created_at=current_admin.created_at or datetime.now(),
            updated_at=current_admin.updated_at
        )
        
        return sanic_json(response.model_dump())
        
    except Exception as e:
        return sanic_json(
            {"error": str(e)}, 
            status=400
        )


@admin_bp.post("/users")
@admin_required
async def create_user(request: Request):
    """Создать пользователя"""
    try:
        # Простая валидация входных данных
        json_data = request.json
        if not json_data:
            return sanic_json({"error": "Отсутствуют данные"}, status=400)
        
        email = json_data.get("email")
        password = json_data.get("password")
        full_name = json_data.get("full_name")
        
        # Базовая валидация
        if not email or "@" not in email:
            return sanic_json({"error": "Некорректный email"}, status=400)
        if not password or len(password) < 6:
            return sanic_json({"error": "Пароль должен быть не менее 6 символов"}, status=400)
        if not full_name or len(full_name) < 2:
            return sanic_json({"error": "Имя должно быть не менее 2 символов"}, status=400)
        
        # Создаем пользователя в базе данных
        created_user = await UserService.create_user(
            email=email,
            password=password,
            full_name=full_name
        )
        
        response = UserResponse(
            id=created_user.id,
            email=created_user.email,
            full_name=created_user.full_name,
            created_at=created_user.created_at or datetime.now(),
            updated_at=created_user.updated_at
        )
        
        return sanic_json(response.model_dump(), status=201)
        
    except ValueError as e:
        return sanic_json(
            {"error": str(e)}, 
            status=409  # Conflict
        )
    except Exception as e:
        return sanic_json(
            {"error": str(e)}, 
            status=400
        )


@admin_bp.get("/users")
@admin_required
async def get_users_list(request: Request):
    """Получить список пользователей"""
    try:
        # Получаем список пользователей из базы данных
        users = await UserService.get_all_users()
        
        users_data = {
            "users": [
                {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                }
                for user in users
            ]
        }
        
        return sanic_json(users_data)
        
    except Exception as e:
        return sanic_json(
            {"error": str(e)}, 
            status=400
        )


@admin_bp.put("/users/<user_id:int>")
@admin_required
async def update_user(request: Request, user_id: int):
    """Обновить пользователя"""
    try:
        # Простая валидация входных данных
        json_data = request.json
        if not json_data:
            return sanic_json({"error": "Отсутствуют данные"}, status=400)
        
        email = json_data.get("email")
        password = json_data.get("password")
        full_name = json_data.get("full_name")
        
        # Базовая валидация (только для присутствующих полей)
        if email is not None and "@" not in email:
            return sanic_json({"error": "Некорректный email"}, status=400)
        if password is not None and len(password) < 6:
            return sanic_json({"error": "Пароль должен быть не менее 6 символов"}, status=400)
        if full_name is not None and len(full_name) < 2:
            return sanic_json({"error": "Имя должно быть не менее 2 символов"}, status=400)
        
        # Обновляем пользователя в базе данных
        updated_user = await UserService.update_user(
            user_id=user_id,
            email=email,
            password=password,
            full_name=full_name
        )
        
        if not updated_user:
            return sanic_json(
                {"error": "Пользователь не найден"}, 
                status=404
            )
        
        response = UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            full_name=updated_user.full_name,
            created_at=updated_user.created_at or datetime.now(),
            updated_at=updated_user.updated_at
        )
        
        return sanic_json(response.model_dump())
        
    except ValueError as e:
        return sanic_json(
            {"error": str(e)}, 
            status=409  # Conflict
        )
    except Exception as e:
        return sanic_json(
            {"error": str(e)}, 
            status=400
        )


@admin_bp.delete("/users/<user_id:int>")
@admin_required
async def delete_user(request: Request, user_id: int):
    """Удалить пользователя"""
    try:
        # Удаляем пользователя из базы данных
        deleted = await UserService.delete_user(user_id)
        
        if not deleted:
            return sanic_json(
                {"error": "Пользователь не найден"}, 
                status=404
            )
        
        return sanic_json({"message": f"Пользователь {user_id} успешно удален"})
        
    except Exception as e:
        return sanic_json(
            {"error": str(e)}, 
            status=400
        )


@admin_bp.get("/users/<user_id:int>/accounts")
@admin_required
async def get_user_accounts_admin(request: Request, user_id: int):
    """Получить список счетов пользователя с балансами (для администратора)"""
    try:
        # Проверяем существование пользователя
        user = await UserService.get_user_by_id(user_id)
        if not user:
            return sanic_json(
                {"error": "Пользователь не найден"}, 
                status=404
            )
        
        # Получаем счета пользователя из базы данных
        accounts = await AccountService.get_user_accounts(user_id)
        
        user_accounts_data = {
            "user_id": user.id,
            "user_email": user.email,
            "user_full_name": user.full_name,
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
        
        return sanic_json(user_accounts_data)
        
    except Exception as e:
        return sanic_json(
            {"error": str(e)}, 
            status=400
        )
