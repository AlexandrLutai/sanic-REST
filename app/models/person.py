from sqlalchemy import Column, String

from .base import BaseModel


class Person(BaseModel):
    """Базовая модель для пользователей и администраторов"""
    
    __abstract__ = True
    
    email = Column(
        String(255), 
        unique=True, 
        nullable=False, 
        index=True
    )
    
    password_hash = Column(
        String(255), 
        nullable=False
    )
    
    full_name = Column(
        String(255), 
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Конвертировать объект в словарь"""
        data = {
            'id': str(self.id),
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
            
        return data
