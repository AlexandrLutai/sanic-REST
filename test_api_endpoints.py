import requests
import json

# Тест 1: Health check
print("=== ТЕСТ 1: Health Check ===")
try:
    response = requests.get("http://localhost:8000/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Ошибка: {e}")

print("\n=== ТЕСТ 2: Вход пользователя ===")
# Тест 2: Вход пользователя
login_data = {
    "email": "test@example.com",
    "password": "testpassword"
}

try:
    response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"Токен получен: {token[:50]}...")
        
        # Тест 3: Получение профиля
        print("\n=== ТЕСТ 3: Профиль пользователя ===")
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = requests.get("http://localhost:8000/api/v1/user/profile", headers=headers)
        print(f"Status: {profile_response.status_code}")
        print(f"Response: {profile_response.text}")
        
        # Тест 4: Получение счетов
        print("\n=== ТЕСТ 4: Счета пользователя ===")
        accounts_response = requests.get("http://localhost:8000/api/v1/user/accounts", headers=headers)
        print(f"Status: {accounts_response.status_code}")
        print(f"Response: {accounts_response.text}")
        
except Exception as e:
    print(f"Ошибка: {e}")

print("\n=== ТЕСТ 5: Вход администратора ===")
# Тест 5: Вход администратора
admin_login_data = {
    "email": "admin@example.com",
    "password": "adminpassword"
}

try:
    response = requests.post("http://localhost:8000/api/v1/auth/admin/login", json=admin_login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        admin_token = response.json().get("access_token")
        print(f"Админ токен получен: {admin_token[:50]}...")
        
        # Тест 6: Список пользователей
        print("\n=== ТЕСТ 6: Список пользователей (админ) ===")
        headers = {"Authorization": f"Bearer {admin_token}"}
        users_response = requests.get("http://localhost:8000/api/v1/admin/users", headers=headers)
        print(f"Status: {users_response.status_code}")
        print(f"Response: {users_response.text}")
        
except Exception as e:
    print(f"Ошибка: {e}")
