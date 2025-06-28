@echo off
echo 🚀 Тестирование Sanic Payment API
echo ================================

echo.
echo 🏥 Тест Health Check:
curl -s http://localhost:8000/health

echo.
echo.
echo 🏠 Тест главной страницы:
curl -s http://localhost:8000/

echo.
echo.
echo 🔐 Тест логина пользователя:
curl -s -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\": \"test@example.com\", \"password\": \"testpassword\"}"

echo.
echo.
echo 👤 Тест профиля пользователя (без токена):
curl -s http://localhost:8000/api/v1/user/profile

echo.
echo.
echo 👨‍💼 Тест админского эндпоинта (без токена):
curl -s http://localhost:8000/api/v1/admin/users

echo.
echo.
echo 🔗 Тест webhook (с правильной подписью):
curl -s -X POST http://localhost:8000/api/v1/webhook/payment -H "Content-Type: application/json" -d "{\"transaction_id\": \"test-123\", \"user_id\": 1, \"account_id\": 1, \"amount\": 100, \"signature\": \"7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8\"}"

echo.
echo.
echo ✅ Тестирование завершено!
pause
