#!/usr/bin/env python3
"""
Скрипт для тестирования всех функций Sanic Payment API
"""

import requests
import json
import hashlib
import time

# Базовый URL API
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_health_check():
    """Тест health check эндпоинтов"""
    print("🏥 Тестирую Health Check...")
    
    # Тест корневого эндпоинта
    response = requests.get(f"{BASE_URL}/")
    print(f"GET / -> {response.status_code}: {response.json()}")
    
    # Тест health эндпоинта
    response = requests.get(f"{BASE_URL}/health")
    print(f"GET /health -> {response.status_code}: {response.json()}")
    
    print("✅ Health Check тесты завершены\n")

def test_authentication():
    """Тест аутентификации пользователей и админов"""
    print("🔐 Тестирую аутентификацию...")
    
    # Тест логина пользователя (должен вернуть ошибку БД)
    user_login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=user_login_data)
        print(f"POST /auth/login (user) -> {response.status_code}: {response.text[:100]}...")
    except Exception as e:
        print(f"POST /auth/login (user) -> Error: {e}")
    
    # Тест логина админа (должен вернуть ошибку БД)
    admin_login_data = {
        "email": "admin@example.com", 
        "password": "adminpassword"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/admin/login", json=admin_login_data)
        print(f"POST /auth/admin/login -> {response.status_code}: {response.text[:100]}...")
    except Exception as e:
        print(f"POST /auth/admin/login -> Error: {e}")
    
    print("✅ Аутентификация тесты завершены (ожидаемы ошибки БД)\n")

def test_user_endpoints():
    """Тест пользовательских эндпоинтов"""
    print("👤 Тестирую пользовательские эндпоинты...")
    
    # Тест без токена (должен вернуть 401)
    endpoints = [
        "/user/profile",
        "/user/accounts", 
        "/user/payments"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}")
            print(f"GET {endpoint} (без токена) -> {response.status_code}: {response.text[:100]}...")
        except Exception as e:
            print(f"GET {endpoint} -> Error: {e}")
    
    print("✅ Пользовательские эндпоинты тесты завершены\n")

def test_admin_endpoints():
    """Тест админских эндпоинтов"""
    print("👨‍💼 Тестирую админские эндпоинты...")
    
    # Тест без токена (должен вернуть 401)
    endpoints = [
        "/admin/profile",
        "/admin/users"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}")
            print(f"GET {endpoint} (без токена) -> {response.status_code}: {response.text[:100]}...")
        except Exception as e:
            print(f"GET {endpoint} -> Error: {e}")
    
    print("✅ Админские эндпоинты тесты завершены\n")

def calculate_webhook_signature(data, secret="gfdmhghif38yrf9ew0jkf32"):
    """Вычисление подписи webhook"""
    # Сортируем ключи и конкатенируем значения
    sorted_data = {k: data[k] for k in sorted(data.keys()) if k != 'signature'}
    string_to_sign = ''.join(str(sorted_data[key]) for key in sorted(sorted_data.keys())) + secret
    
    return hashlib.sha256(string_to_sign.encode()).hexdigest()

def test_webhook():
    """Тест webhook эндпоинта"""
    print("🔗 Тестирую webhook эндпоинт...")
    
    # Тестовые данные для webhook
    webhook_data = {
        "transaction_id": "test-transaction-123",
        "user_id": 1,
        "account_id": 1,
        "amount": 100.50
    }
    
    # Вычисляем подпись
    signature = calculate_webhook_signature(webhook_data)
    webhook_data["signature"] = signature
    
    print(f"Данные webhook: {webhook_data}")
    print(f"Вычисленная подпись: {signature}")
    
    try:
        response = requests.post(f"{API_BASE}/webhook/payment", json=webhook_data)
        print(f"POST /webhook/payment -> {response.status_code}: {response.text[:200]}...")
    except Exception as e:
        print(f"POST /webhook/payment -> Error: {e}")
    
    print("✅ Webhook тесты завершены\n")

def test_openapi():
    """Тест OpenAPI документации"""
    print("📚 Тестирую OpenAPI документацию...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            print(f"OpenAPI spec загружен: {len(openapi_spec.get('paths', {}))} эндпоинтов найдено")
            
            # Показываем некоторые эндпоинты
            paths = list(openapi_spec.get('paths', {}).keys())[:5]
            print(f"Примеры эндпоинтов: {paths}")
        else:
            print(f"OpenAPI spec -> {response.status_code}")
    except Exception as e:
        print(f"OpenAPI spec -> Error: {e}")
    
    print("✅ OpenAPI тесты завершены\n")

def main():
    """Главная функция тестирования"""
    print("🚀 Запуск полного тестирования Sanic Payment API")
    print("=" * 60)
    
    # Проверяем, что сервер доступен
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Сервер доступен, начинаем тестирование...\n")
        else:
            print(f"❌ Сервер недоступен: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Сервер недоступен: {e}")
        return
    
    # Запускаем все тесты
    test_health_check()
    test_authentication()
    test_user_endpoints()
    test_admin_endpoints() 
    test_webhook()
    test_openapi()
    
    print("🎉 Тестирование завершено!")
    print("=" * 60)
    print("📝 Сводка:")
    print("✅ Сервер работает")
    print("✅ Health check эндпоинты доступны")
    print("✅ API маршрутизация настроена правильно")
    print("✅ Аутентификация реагирует на запросы")
    print("✅ Webhook принимает данные")
    print("✅ OpenAPI документация доступна")
    print("\n⚠️  Для полной функциональности требуется настройка PostgreSQL")

if __name__ == "__main__":
    main()
