"""Add test data for user and admin

Revision ID: b1f1e8214cf1
Revises: 20322cfd5a3d
Create Date: 2025-06-27 18:38:22.669749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1f1e8214cf1'
down_revision: Union[str, None] = '20322cfd5a3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем тестового пользователя
    op.execute("""
        INSERT INTO users (id, email, password_hash, full_name, created_at) 
        VALUES (1, 'user@test.com', '$2b$12$SwGzZGLxejbmYA09qJGfROKutmzpBHwBjS1r/DgiTFG7GSbrmssKS', 'Test User', NOW())
    """)
    
    # Создаем тестового администратора
    op.execute("""
        INSERT INTO admins (id, email, password_hash, full_name, created_at) 
        VALUES (1, 'admin@test.com', '$2b$12$xfOxkibSs61eBb7jkgdZveW.u0UXR8okgowdaApGWM0iUOp/tqrQK', 'Test Admin', NOW())
    """)
    
    # Создаем тестовый счет для пользователя
    op.execute("""
        INSERT INTO accounts (id, user_id, account_number, balance, currency, created_at) 
        VALUES (1, 1, 'ACC1000000001', 1000.00, 'RUB', NOW())
    """)


def downgrade() -> None:
    # Удаляем тестовые данные в обратном порядке
    op.execute("DELETE FROM accounts WHERE id = 1")
    op.execute("DELETE FROM admins WHERE id = 1") 
    op.execute("DELETE FROM users WHERE id = 1")
