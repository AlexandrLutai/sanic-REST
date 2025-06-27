"""Сервисы для работы с пользователями"""

from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from ..models.user import User
from ..models.account import Account
from ..models.payment import Payment
from ..database import get_db_session
from ..auth.service import PasswordManager


class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_users() -> List[User]:
        """Получить список всех пользователей"""
        async with get_db_session() as session:
            result = await session.execute(select(User))
            return result.scalars().all()
    
    @staticmethod
    async def create_user(email: str, password: str, full_name: str) -> User:
        """Создать нового пользователя"""
        async with get_db_session() as session:
            # Проверяем существование пользователя с таким email
            existing_user = await session.execute(
                select(User).where(User.email == email)
            )
            if existing_user.scalar_one_or_none():
                raise ValueError("Пользователь с таким email уже существует")
            
            # Хешируем пароль
            hashed_password = PasswordManager.hash_password(password)
            
            # Создаем пользователя
            user = User(
                email=email,
                password_hash=hashed_password,
                full_name=full_name
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            return user
    
    @staticmethod
    async def update_user(user_id: int, email: Optional[str] = None, 
                         password: Optional[str] = None, 
                         full_name: Optional[str] = None) -> Optional[User]:
        """Обновить пользователя"""
        async with get_db_session() as session:
            # Проверяем существование пользователя
            user = await session.get(User, user_id)
            if not user:
                return None
            
            # Проверяем email на уникальность (если он изменяется)
            if email and email != user.email:
                existing_user = await session.execute(
                    select(User).where(User.email == email)
                )
                if existing_user.scalar_one_or_none():
                    raise ValueError("Пользователь с таким email уже существует")
                user.email = email
            
            # Обновляем поля
            if password:
                user.password_hash = PasswordManager.hash_password(password)
            if full_name:
                user.full_name = full_name
            
            await session.commit()
            await session.refresh(user)
            
            return user
    
    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """Удалить пользователя"""
        async with get_db_session() as session:
            user = await session.get(User, user_id)
            if not user:
                return False
            
            await session.delete(user)
            await session.commit()
            
            return True


class AccountService:
    """Сервис для работы со счетами"""
    
    @staticmethod
    async def get_user_accounts(user_id: int) -> List[Account]:
        """Получить счета пользователя"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Account).where(Account.user_id == user_id)
            )
            return result.scalars().all()
    
    @staticmethod
    async def get_account_by_id(account_id: int) -> Optional[Account]:
        """Получить счет по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Account).where(Account.id == account_id)
            )
            return result.scalar_one_or_none()


class PaymentService:
    """Сервис для работы с платежами"""
    
    @staticmethod
    async def get_user_payments(user_id: int) -> List[Payment]:
        """Получить платежи пользователя"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Payment).where(Payment.user_id == user_id)
            )
            return result.scalars().all()
