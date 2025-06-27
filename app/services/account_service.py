"""Сервисы для работы со счетами"""

from typing import List, Optional
from sqlalchemy import select

from ..models.account import Account
from ..database import get_db_session


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
    
    @staticmethod
    async def create_account(user_id: int, account_id: int = None) -> Account:
        """Создать новый счет для пользователя"""
        async with get_db_session() as session:
            account = Account(
                user_id=user_id,
                balance=0
            )
            # Если передан конкретный account_id, используем его
            if account_id:
                account.id = account_id
            
            session.add(account)
            await session.commit()
            await session.refresh(account)
            return account
    
    @staticmethod
    async def add_to_balance(account_id: int, amount) -> Account:
        """Добавить средства на счет"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Account).where(Account.id == account_id)
            )
            account = result.scalar_one_or_none()
            
            if not account:
                raise ValueError("Счет не найден")
            
            from decimal import Decimal
            account.balance += Decimal(str(amount))  # Конвертируем в Decimal
            await session.commit()
            await session.refresh(account)
            return account
    
    @staticmethod
    async def get_account_by_user_and_id(user_id: int, account_id: int) -> Optional[Account]:
        """Получить счет по ID пользователя и ID счета"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Account).where(
                    Account.id == account_id,
                    Account.user_id == user_id
                )
            )
            return result.scalar_one_or_none()
