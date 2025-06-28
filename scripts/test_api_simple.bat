@echo off
echo === ТЕСТ API ENDPOINTS ===

echo.
echo === 1. Health Check ===
curl -X GET http://localhost:8000/health
echo.

echo.
echo === 2. Вход пользователя ===
curl -X POST http://localhost:8000/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"test@example.com\", \"password\": \"testpassword\"}"
echo.

echo.
echo === 3. Вход администратора ===
curl -X POST http://localhost:8000/api/v1/auth/admin/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"admin@example.com\", \"password\": \"adminpassword\"}"
echo.

pause
