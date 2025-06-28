import asyncio
import sqlite3
from passlib.context import CryptContext
from datetime import datetime

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_test_users():
    """Создаем тестовых пользователей в SQLite базе"""
    
    # Подключаемся к SQLite базе
    conn = sqlite3.connect('./test.db')
    cursor = conn.cursor()
    
    try:
        print("🔧 Создание тестовых пользователей...")
        
        # Проверяем, существуют ли таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Найденные таблицы: {[table[0] for table in tables]}")
        
        if not tables:
            print("❌ Таблицы не найдены. Создаем базовую структуру...")
            
            # Создаем таблицы (упрощенная версия)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    account_number VARCHAR(50) UNIQUE NOT NULL,
                    balance DECIMAL(15, 2) DEFAULT 0.00,
                    currency VARCHAR(3) DEFAULT 'RUB',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            print("✅ Таблицы созданы")
        
        # Хешируем пароли
        user_password_hash = pwd_context.hash("testpassword")
        admin_password_hash = pwd_context.hash("adminpassword")
        
        # Добавляем тестового пользователя
        cursor.execute('''
            INSERT OR REPLACE INTO users (id, email, password_hash, full_name, created_at)
            VALUES (1, 'user@test.com', ?, 'Test User', CURRENT_TIMESTAMP)
        ''', (user_password_hash,))
        
        # Добавляем тестового администратора
        cursor.execute('''
            INSERT OR REPLACE INTO admins (id, email, password_hash, full_name, created_at)
            VALUES (1, 'admin@test.com', ?, 'Test Admin', CURRENT_TIMESTAMP)
        ''', (admin_password_hash,))
        
        # Добавляем тестовый счет
        cursor.execute('''
            INSERT OR REPLACE INTO accounts (id, user_id, account_number, balance, currency, created_at)
            VALUES (1, 1, 'ACC1000000001', 1000.00, 'RUB', CURRENT_TIMESTAMP)
        ''')
        
        conn.commit()
        print("✅ Тестовые пользователи созданы:")
        print("   👤 user@test.com / testpassword")
        print("   🔧 admin@test.com / adminpassword")
        print("   💰 Счет: ACC1000000001, баланс: 1000.00 RUB")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    asyncio.run(create_test_users())
