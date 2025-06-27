import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from functools import wraps

from sanic import Request
from sanic.response import json as sanic_json
from sqlalchemy import select

from ..models.user import User
from ..models.admin import Admin
from ..database import get_db_session


class JWTManager:
    """Менеджер для работы с JWT токенами"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def generate_token(self, user_id: int, user_type: str, expires_in: int = 3600) -> str:
        """Генерация JWT токена"""
        payload = {
            "user_id": user_id,
            "user_type": user_type,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in),
            "iat": datetime.now(timezone.utc)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> dict:
        """Декодирование JWT токена"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Токен истек")
        except jwt.InvalidTokenError:
            raise ValueError("Недействительный токен")


class PasswordManager:
    """Менеджер для работы с паролями"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширование пароля"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


class AuthService:
    """Сервис аутентификации"""
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        async with get_db_session() as session:
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            
            if user and PasswordManager.verify_password(password, user.password_hash):
                return user
            
            return None
    
    @staticmethod
    async def authenticate_admin(email: str, password: str) -> Optional[Admin]:
        """Аутентификация администратора"""
        async with get_db_session() as session:
            result = await session.execute(select(Admin).where(Admin.email == email))
            admin = result.scalar_one_or_none()
            
            if admin and PasswordManager.verify_password(password, admin.password_hash):
                return admin
            
            return None
    
    @staticmethod
    async def register_user(email: str, password: str, full_name: str) -> User:
        """Регистрация нового пользователя"""
        async with get_db_session() as session:
            existing_user = await session.execute(select(User).where(User.email == email))
            if existing_user.scalar_one_or_none():
                raise ValueError("Пользователь с таким email уже существует")
            
            hashed_password = PasswordManager.hash_password(password)
            
            user = User(
                email=email,
                password_hash=hashed_password,
                full_name=full_name
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            return user


def get_jwt_manager(request: Request) -> JWTManager:
    """Получение менеджера JWT из конфигурации приложения"""
    return JWTManager(
        secret_key=request.app.config.get("JWT_SECRET"),
        algorithm=request.app.config.get("JWT_ALGORITHM", "HS256")
    )


def extract_token(request: Request) -> str:
    """Извлечение токена из заголовка Authorization"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise ValueError("Отсутствует заголовок Authorization")
    
    if not auth_header.startswith("Bearer "):
        raise ValueError("Неверный формат токена")
    
    return auth_header[7:]


async def get_current_user(request: Request) -> Union[User, Admin]:
    """Получение текущего пользователя из токена"""
    try:
        token = extract_token(request)
        jwt_manager = get_jwt_manager(request)
        payload = jwt_manager.decode_token(token)
        
        user_id = payload.get("user_id")
        user_type = payload.get("user_type")
        
        if not user_id or not user_type:
            raise ValueError("Недействительный токен")
        
        async with get_db_session() as session:
            if user_type == "user":
                result = await session.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()
            elif user_type == "admin":
                result = await session.execute(select(Admin).where(Admin.id == user_id))
                user = result.scalar_one_or_none()
            else:
                raise ValueError("Неизвестный тип пользователя")
            
            if not user:
                raise ValueError("Пользователь не найден")
            
            return user
            
    except Exception as e:
        raise ValueError(f"Ошибка аутентификации: {str(e)}")


def auth_required(user_types=None):
    """Декоратор для проверки аутентификации"""
    if user_types is None:
        user_types = ["user", "admin"]
    
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            try:
                user = await get_current_user(request)
                
                user_type = "admin" if isinstance(user, Admin) else "user"
                if user_type not in user_types:
                    return sanic_json(
                        {"error": "Недостаточно прав доступа"}, 
                        status=403
                    )
                
                request.ctx.current_user = user
                request.ctx.user_type = user_type
                
                return await f(request, *args, **kwargs)
                
            except ValueError as e:
                return sanic_json(
                    {"error": str(e)}, 
                    status=401
                )
            except Exception as e:
                return sanic_json(
                    {"error": "Внутренняя ошибка сервера"}, 
                    status=500
                )
        
        return decorated_function
    return decorator


def admin_required(f):
    """Декоратор для проверки прав администратора"""
    return auth_required(user_types=["admin"])(f)


def user_required(f):
    """Декоратор для проверки прав пользователя"""
    return auth_required(user_types=["user"])(f)
