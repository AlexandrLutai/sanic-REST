from sqlalchemy import Column, String, Numeric, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from decimal import Decimal
import enum

from .base import BaseModel


class PaymentStatus(enum.Enum):
    """Статусы платежа"""
    PENDING = "pending"      
    COMPLETED = "completed"  
    FAILED = "failed"        
    CANCELLED = "cancelled"  


class PaymentType(enum.Enum):
    """Типы платежей"""
    DEPOSIT = "deposit"      
    WITHDRAWAL = "withdrawal"  
    TRANSFER = "transfer"   

class Payment(BaseModel):
    """Модель платежа/транзакции"""
    
    __tablename__ = "payments"
    
    
    transaction_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Уникальный идентификатор транзакции из внешней системы"
    )
    
    account_id = Column(
        ForeignKey("accounts.id"),
        nullable=False,
        index=True
    )
    
    user_id = Column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    amount = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Сумма платежа"
    )
    
   
    currency = Column(
        String(3),
        nullable=False,
        default="RUB"
    )
    
    payment_type = Column(
        Enum(PaymentType),
        nullable=False,
        default=PaymentType.DEPOSIT
    )
    
    status = Column(
        Enum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.PENDING
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Описание платежа"
    )
    
    
    target_account_id = Column(
        ForeignKey("accounts.id"),
        nullable=True,
        index=True,
        comment="Целевой счет для переводов"
    )
    
    
    external_data = Column(
        Text,
        nullable=True,
        comment="Дополнительные данные от внешней системы (JSON)"
    )
    
    
    account = relationship("Account", foreign_keys=[account_id], back_populates="payments")
    user = relationship("User", back_populates="payments")
    target_account = relationship("Account", foreign_keys=[target_account_id])
    
    def __init__(self, **kwargs):
        """Инициализатор с правильной обработкой amount и currency"""
        if 'amount' in kwargs and kwargs['amount'] is not None:
            kwargs['amount'] = Decimal(str(kwargs['amount']))
        if 'currency' not in kwargs or kwargs['currency'] is None:
            kwargs['currency'] = 'RUB'
        if 'payment_type' not in kwargs or kwargs['payment_type'] is None:
            kwargs['payment_type'] = PaymentType.DEPOSIT
        if 'status' not in kwargs or kwargs['status'] is None:
            kwargs['status'] = PaymentStatus.PENDING
        super().__init__(**kwargs)
    
    def validate_account_user_consistency(self, account_user_id: int = None) -> None:
        """Проверить согласованность account_id и user_id"""
        if account_user_id is not None:
            if self.user_id != account_user_id:
                raise ValueError(f"Payment.user_id ({self.user_id}) не соответствует Account.user_id ({account_user_id})")
    
    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, transaction_id='{self.transaction_id}', amount={self.amount}, status='{self.status.value}')>"
    
    def to_dict(self) -> dict:
        """Конвертировать платеж в словарь"""
        return {
            'id': str(self.id),
            'transaction_id': self.transaction_id,
            'account_id': str(self.account_id),
            'user_id': str(self.user_id),
            'amount': float(self.amount),
            'currency': self.currency,
            'payment_type': self.payment_type.value,
            'status': self.status.value,
            'description': self.description,
            'target_account_id': str(self.target_account_id) if self.target_account_id else None,
            'external_data': self.external_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    
    def is_pending(self) -> bool:
        """Проверить, находится ли платеж в статусе ожидания"""
        return self.status == PaymentStatus.PENDING
    
    def is_completed(self) -> bool:
        """Проверить, завершен ли платеж успешно"""
        return self.status == PaymentStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Проверить, завершился ли платеж с ошибкой"""
        return self.status == PaymentStatus.FAILED
    
    def can_be_processed(self) -> bool:
        """Проверить, можно ли обработать платеж"""
        return self.status == PaymentStatus.PENDING
    
    def can_be_cancelled(self) -> bool:
        """Проверить, можно ли отменить платеж"""
        return self.status in [PaymentStatus.PENDING, PaymentStatus.FAILED]
    
    
    def mark_completed(self) -> None:
        """Отметить платеж как успешно завершенный"""
        if not self.can_be_processed():
            raise ValueError("Можно завершить только платеж в статусе 'pending'")
        self.status = PaymentStatus.COMPLETED
    
    def mark_failed(self, reason: str = None) -> None:
        """Отметить платеж как неудачный"""
        if not self.can_be_processed():
            raise ValueError("Можно отметить как неудачный только платеж в статусе 'pending'")
        self.status = PaymentStatus.FAILED
        if reason:
            self.description = f"Ошибка: {reason}"
    
    def cancel(self, reason: str = None) -> None:
        """Отменить платеж"""
        if not self.can_be_cancelled():
            raise ValueError("Можно отменить только платеж в статусе 'pending' или 'failed'")
        self.status = PaymentStatus.CANCELLED
        if reason:
            self.description = f"Отменен: {reason}"
    
  
    @classmethod
    def create_deposit(cls, transaction_id: str, account_id: int, user_id: int, 
                      amount: float, currency: str = "RUB", 
                      description: str = None, external_data: str = None) -> "Payment":
        """Создать платеж пополнения (например, из веб-хука)"""
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        
        return cls(
            transaction_id=transaction_id,
            account_id=account_id,
            user_id=user_id,
            amount=amount,
            currency=currency,
            payment_type=PaymentType.DEPOSIT,
            description=description or "Пополнение счета",
            external_data=external_data
        )
    
    @classmethod
    def create_withdrawal(cls, transaction_id: str, account_id: int, user_id: int, 
                         amount: float, currency: str = "RUB", 
                         description: str = None) -> "Payment":
        """Создать платеж списания/вывода"""
        if amount <= 0:
            raise ValueError("Сумма списания должна быть положительной")
        
        return cls(
            transaction_id=transaction_id,
            account_id=account_id,
            user_id=user_id,
            amount=amount,
            currency=currency,
            payment_type=PaymentType.WITHDRAWAL,
            description=description or "Списание со счета"
        )
    
    @classmethod
    def create_transfer(cls, transaction_id: str, from_account_id: int, 
                       to_account_id: int, user_id: int, amount: float, 
                       currency: str = "RUB", description: str = None) -> "Payment":
        """Создать платеж перевода между счетами"""
        if amount <= 0:
            raise ValueError("Сумма перевода должна быть положительной")
        if from_account_id == to_account_id:
            raise ValueError("Нельзя переводить на тот же счет")
        
        return cls(
            transaction_id=transaction_id,
            account_id=from_account_id,
            user_id=user_id,
            amount=amount,
            currency=currency,
            payment_type=PaymentType.TRANSFER,
            target_account_id=to_account_id,
            description=description or f"Перевод на счет {to_account_id}"
        )
    
    @classmethod
    def create_with_validation(cls, transaction_id: str, account_id: int, 
                              account_user_id: int, amount: float, 
                              currency: str = "RUB", description: str = None, 
                              external_data: str = None) -> "Payment":
        """Создать платеж с валидацией согласованности account-user"""
        payment = cls.create_deposit(
            transaction_id=transaction_id,
            account_id=account_id,
            user_id=account_user_id,  # используем проверенный user_id из account
            amount=amount,
            currency=currency,
            description=description,
            external_data=external_data
        )
        payment.validate_account_user_consistency(account_user_id)
        return payment
    
    def get_webhook_data(self) -> dict:
        """Получить данные в формате веб-хука (для тестирования)"""
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "account_id": self.account_id,
            "amount": float(self.amount)
        }
