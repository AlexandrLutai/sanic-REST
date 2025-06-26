from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseModel(Base):
    """
    Базовая модель, от которой наследуются все остальные модели.
    Содержит общие поля, которые есть у всех сущностей в системе.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())