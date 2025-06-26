from sqlalchemy.orm import relationship

from .person import Person


class User(Person):
    """Модель пользователя системы"""
    
    __tablename__ = "users"
    
    accounts = relationship("Account", back_populates="user", lazy="selectin")
    # payments = relationship("Payment", back_populates="user", lazy="select")
