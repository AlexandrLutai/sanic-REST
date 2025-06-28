import requests
import json

# Базовый URL API
BASE_URL = "http://localhost:8000"

def test_health():
    """Тест health endpoint"""
    print("=== Тестирование Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_user_login():
    """Тест авторизации пользователя"""
    print("=== Тестирование User Login ===")
    login_data = {
        "email": "user@test.com",
        "password": "testpassword"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print()
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("token", {}).get("access_token")
        return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

def test_admin_login():
    """Тест авторизации администратора"""
    print("=== Тестирование Admin Login ===")
    login_data = {
        "email": "admin@test.com",
        "password": "adminpassword"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/admin/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print()
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("token", {}).get("access_token")
        return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

def test_user_profile(token):
    """Тест получения профиля пользователя"""
    if not token:
        print("=== Тестирование User Profile: ПРОПУЩЕНО (нет токена) ===")
        return
    
    print("=== Тестирование User Profile ===")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/user/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print()
    except Exception as e:
        print(f"Ошибка: {e}")

def test_webhook():
    """Тест webhook endpoint"""
    print("=== Тестирование Webhook ===")
    webhook_data = {
        "transaction_id": "test-transaction-001",
        "user_id": 1,
        "account_id": 1,
        "amount": 50.00,
        "signature": "test-signature"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/payment",
            json=webhook_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print()
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    print("🚀 Тестирование Sanic Payment API")
    print("=" * 50)
    
    # Тестируем health
    health_ok = test_health()
    
    if not health_ok:
        print("❌ API недоступен, завершаем тесты")
        exit(1)
    
    # Тестируем авторизацию
    user_token = test_user_login()
    admin_token = test_admin_login()
    
    # Тестируем профиль пользователя
    test_user_profile(user_token)
    
    # Тестируем webhook
    test_webhook()
    
    print("✅ Тестирование завершено")
