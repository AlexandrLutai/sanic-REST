# Sanic Payment API

REST API приложение для управления пользователями, счетами и платежами, реализованное на Sanic с асинхронной поддержкой.

## Стек технологий

- **Python 3.11+**
- **Sanic** - веб-фреймворк
- **SQLAlchemy** (async) - ORM для работы с БД
- **PostgreSQL** - база данных
- **Alembic** - миграции БД
- **Pydantic** - валидация схем
- **Docker & Docker Compose** - контейнеризация
- **pytest** - тестирование

## Быстрый старт

### Вариант 1: Запуск с Docker Compose (рекомендуемый)

Docker Compose автоматически развернет PostgreSQL и приложение:

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/AlexandrLutai/sanic-REST
   cd sanic
   ```

2. **Запустите приложение:**
   ```bash
   docker-compose -f docker/docker-compose.yml up --build
   ```

3. **Приложение будет доступно по адресу:** `http://localhost:8000`

4. **Для остановки:**
   ```bash
   docker-compose -f docker/docker-compose.yml down
   ```

### Вариант 2: Локальный запуск (без Docker)

1. **Установите PostgreSQL** и создайте базу данных:
   ```sql
   CREATE DATABASE sanic_payment_db;
   CREATE USER postgres WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE sanic_payment_db TO postgres;
   ```

2. **Установите Python зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте переменные окружения:**
   Скопируйте `.env.example` в `.env` и настройте под вашу БД:
   ```bash
   cp config/.env.example .env
   ```
   
   Отредактируйте `.env`:
   ```bash
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=password
   DB_NAME=sanic_payment_db
   ```

4. **Примените миграции:**
   ```bash
   alembic -c config/alembic.ini upgrade head
   ```

5. **Запустите приложение:**
   ```bash
   python -m app.main
   ```

## Тестовые данные

После применения миграций в БД автоматически создаются тестовые пользователи:

### Тестовый пользователь
- **Email:** `user@test.com`
- **Password:** `testpassword`
- **ID:** 1
- **Счет ID:** 1 (баланс: 1000.00 RUB)

### Тестовый администратор
- **Email:** `admin@test.com`
- **Password:** `adminpassword`
- **ID:** 1

## API Endpoints

### Аутентификация

#### POST `/api/v1/auth/login` - Вход пользователя
```json
{
  "email": "user@test.com",
  "password": "testpassword"
}
```

#### POST `/api/v1/auth/admin/login` - Вход администратора
```json
{
  "email": "admin@test.com",
  "password": "adminpassword"
}
```

### Пользователь

#### GET `/api/v1/user/profile` - Профиль пользователя
**Headers:** `Authorization: Bearer <token>`

#### GET `/api/v1/user/accounts` - Счета пользователя
**Headers:** `Authorization: Bearer <token>`

#### GET `/api/v1/user/payments` - Платежи пользователя
**Headers:** `Authorization: Bearer <token>`

### Администратор

#### GET `/api/v1/admin/profile` - Профиль администратора
**Headers:** `Authorization: Bearer <token>`

#### GET `/api/v1/admin/users` - Список всех пользователей
**Headers:** `Authorization: Bearer <token>`

#### POST `/api/v1/admin/users` - Создать пользователя
**Headers:** `Authorization: Bearer <token>`
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "New User"
}
```

#### PUT `/api/v1/admin/users/{user_id}` - Обновить пользователя
**Headers:** `Authorization: Bearer <token>`
```json
{
  "email": "updated@example.com",
  "full_name": "Updated Name"
}
```

#### DELETE `/api/v1/admin/users/{user_id}` - Удалить пользователя
**Headers:** `Authorization: Bearer <token>`

#### GET `/api/v1/admin/users/{user_id}/accounts` - Счета пользователя
**Headers:** `Authorization: Bearer <token>`

### Webhook

#### POST `/api/v1/webhook/payment` - Обработка платежа
```json
{
  "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
  "user_id": 1,
  "account_id": 1,
  "amount": 100,
  "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
}
```

**Подпись формируется:** SHA256(`{account_id}{amount}{transaction_id}{user_id}{secret_key}`)

## Примеры запросов

### 1. Вход пользователя
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@test.com", "password": "testpassword"}'
```

### 2. Получение профиля (с токеном)
```bash
curl -X GET http://localhost:8000/api/v1/user/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Получение счетов пользователя
```bash
curl -X GET http://localhost:8000/api/v1/user/accounts \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Обработка webhook платежа
```bash
curl -X POST http://localhost:8000/api/v1/webhook/payment \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "test-transaction-001", 
    "user_id": 1, 
    "account_id": 1, 
    "amount": 50.00, 
    "signature": "CALCULATED_SIGNATURE"
  }'
```

## Разработка

### Запуск тестов
```bash
pytest tests/ -v
```

### Создание новой миграции
```bash
alembic -c config/alembic.ini revision --autogenerate -m "Description"
```

### Применение миграций
```bash
alembic -c config/alembic.ini upgrade head
```

### Проверка покрытия тестами
```bash
pytest --cov=app tests/
```

## Структура проекта

```
sanic/
├── app/
│   ├── __init__.py
│   ├── main.py              # Точка входа
│   ├── models/              # SQLAlchemy модели
│   ├── routes/              # API маршруты
│   ├── services/            # Бизнес-логика
│   ├── schemas/             # Pydantic схемы
│   ├── auth/                # Аутентификация
│   └── database/            # Конфигурация БД
├── migrations/              # Alembic миграции
├── tests/                   # Тесты
├── docker/                  # Docker файлы
│   ├── docker-compose.yml   # PostgreSQL + App сервисы
│   ├── Dockerfile          # Docker образ приложения
│   └── Dockerfile.simple   # Упрощенный Docker образ
├── config/                  # Конфигурационные файлы
│   ├── alembic.ini         # Настройки Alembic
│   └── .env.example        # Пример переменных окружения
├── docs/                    # Документация
├── scripts/                 # Служебные скрипты
├── requirements.txt        # Python зависимости
└── README.md               # Документация
```

## Docker Compose конфигурация

Проект включает полную Docker Compose конфигурацию с двумя сервисами:

### Сервис PostgreSQL (`db`)
- **Образ:** `postgres:15-alpine`
- **База данных:** `sanic_payment_db`
- **Пользователь:** `postgres`
- **Пароль:** `password`
- **Порт:** `5432`
- **Health check:** автоматическая проверка готовности БД

### Сервис приложения (`app`)
- **Сборка:** из локального Dockerfile
- **Зависимости:** ожидает готовности PostgreSQL
- **Порт:** `8000`
- **Автоматическое применение миграций** при запуске

## Переменные окружения

```bash
# Основные настройки
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false

# База данных
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sanic_payment_api
DB_USER=postgres
DB_PASSWORD=postgres

# Безопасность
JWT_SECRET=your-secret-key
WEBHOOK_SECRET=gfdmhghif38yrf9ew0jkf32
```

## Health Check

**GET** `/health` - проверка состояния приложения

```bash
curl http://localhost:8000/health
```

## Проверка работы API

После запуска проекта можно проверить работу API:

1. **Проверка здоровья приложения:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Авторизация пользователя:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "user@test.com", "password": "testpassword"}'
   ```

3. **Авторизация администратора:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/admin/login \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@test.com", "password": "adminpassword"}'
   ```







