"""Сервисы для работы с платежами"""

from typing import List, Optional
from sqlalchemy import select

from ..models.payment import Payment
from ..database import get_db_session


class PaymentService:
    """Сервис для работы с платежами"""
    
    @staticmethod
    async def get_user_payments(user_id: int) -> List[Payment]:
        """Получить платежи пользователя"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Payment).where(Payment.user_id == user_id)
                .order_by(Payment.created_at.desc())
            )
            return result.scalars().all()
    
    @staticmethod
    async def get_payment_by_transaction_id(transaction_id: str) -> Optional[Payment]:
        """Получить платеж по ID транзакции"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Payment).where(Payment.transaction_id == transaction_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def create_payment(transaction_id: str, account_id: int, user_id: int, amount) -> Payment:
        """Создать новый платеж"""
        async with get_db_session() as session:
            payment = Payment(
                transaction_id=transaction_id,
                account_id=account_id,
                user_id=user_id,
                amount=amount
            )
            session.add(payment)
            await session.commit()
            await session.refresh(payment)
            return payment
    
    @staticmethod
    async def get_account_payments(account_id: int) -> List[Payment]:
        """Получить платежи по конкретному счету"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Payment).where(Payment.account_id == account_id)
                .order_by(Payment.created_at.desc())
            )
            return result.scalars().all()
    
    @staticmethod
    async def get_payment_by_id(payment_id: int) -> Optional[Payment]:
        """Получить платеж по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Payment).where(Payment.id == payment_id)
            )
            return result.scalar_one_or_none()
