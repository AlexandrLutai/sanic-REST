from sanic import Sanic
from sanic.response import json as sanic_json
from sanic_cors import CORS

from app.database import create_tables, close_db, db_config


def create_app():
    """Создание и настройка Sanic приложения"""
    app = Sanic("SanicPaymentAPI")
    
    CORS(app)
    
    app.config.update({
        "DATABASE_URL": db_config.DATABASE_URL,
        "SECRET_KEY": "your-secret-key-change-in-production",
        "JWT_SECRET": "jwt-secret-key-change-in-production",
        "JWT_ALGORITHM": "HS256",
        "JWT_ACCESS_TOKEN_EXPIRES": 3600,
        "WEBHOOK_SECRET": "webhook-secret-key",
    })
    
    @app.before_server_start
    async def initialize_db(app, loop):
        """Инициализация базы данных при запуске"""
        await create_tables()
    
    @app.after_server_stop
    async def close_database(app, loop):
        """Закрытие соединения с БД при остановке"""
        await close_db()
    
    @app.get("/")
    async def health_check(request):
        """Проверка работоспособности API"""
        return sanic_json({
            "status": "ok",
            "message": "Sanic Payment API is running",
            "version": "1.0.0"
        })
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
