from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from decimal import Decimal

from .base import BaseModel


class Account(BaseModel):
    """Модель счета пользователя"""
    
    __tablename__ = "accounts"
    
    user_id = Column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    account_number = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )
    
    balance = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00')
    )
    
    currency = Column(
        String(3),
        nullable=False,
        default="RUB"
    )
    
    user = relationship("User", back_populates="accounts")
    payments = relationship("Payment", foreign_keys="Payment.account_id", back_populates="account", lazy="selectin")
    
    def __init__(self, **kwargs):
        """Инициализатор с правильной обработкой balance и currency"""
        if 'balance' in kwargs and kwargs['balance'] is not None:
            kwargs['balance'] = Decimal(str(kwargs['balance']))
        elif 'balance' not in kwargs:
            kwargs['balance'] = Decimal('0.00')
        if 'currency' not in kwargs or kwargs['currency'] is None:
            kwargs['currency'] = 'RUB'
        super().__init__(**kwargs)
    
    def __repr__(self) -> str:
        return f"<Account(id={self.id}, account_number='{self.account_number}', balance={self.balance}, currency='{self.currency}')>"
    
    def to_dict(self) -> dict:
        """Конвертировать счет в словарь"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'account_number': self.account_number,
            'balance': float(self.balance),
            'currency': self.currency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def add_funds(self, amount: float) -> None:
        """Пополнить баланс счета"""
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self.balance += Decimal(str(amount))
    
    def withdraw_funds(self, amount: float) -> None:
        """Списать средства со счета"""
        if amount <= 0:
            raise ValueError("Сумма списания должна быть положительной")
        amount_decimal = Decimal(str(amount))
        if self.balance < amount_decimal:
            raise ValueError("Недостаточно средств на счете")
        self.balance -= amount_decimal
    
    def has_sufficient_balance(self, amount: float) -> bool:
        """Проверить достаточность средств"""
        return self.balance >= Decimal(str(amount))
