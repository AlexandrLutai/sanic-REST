from .person import Person


class Admin(Person):
    """Модель администратора системы"""
    
    __tablename__ = "admins"
