from sanic import Sanic
from sanic.response import json as sanic_json
from sanic_cors import CORS
import os
from dotenv import load_dotenv

from app.database import create_tables, close_db, db_config
from app.routes.auth import auth_bp
from app.routes.user import user_bp
from app.routes.admin import admin_bp
from app.routes.webhook import webhook_bp

# Загружаем переменные окружения
load_dotenv()


def create_app():
    """Создание и настройка Sanic приложения"""
    app = Sanic("SanicPaymentAPI")
    
    CORS(app)
    
    app.config.update({
        "DATABASE_URL": db_config.DATABASE_URL,
        "SECRET_KEY": os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
        "JWT_SECRET": os.getenv("JWT_SECRET", "jwt-secret-key-change-in-production"),
        "JWT_ALGORITHM": os.getenv("JWT_ALGORITHM", "HS256"),
        "JWT_ACCESS_TOKEN_EXPIRES": int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600")),
        "WEBHOOK_SECRET": os.getenv("WEBHOOK_SECRET", "gfdmhghif38yrf9ew0jkf32"),
    })
    
    @app.before_server_start
    async def initialize_db(app, loop):
        """Инициализация базы данных при запуске"""
        await create_tables()
        print("Database initialized successfully!")
    
    @app.after_server_stop
    async def close_database(app, loop):
        """Закрытие соединения с БД при остановке"""
        await close_db()
    
    # Регистрируем blueprint'ы
    app.blueprint(auth_bp)
    app.blueprint(user_bp)
    app.blueprint(admin_bp)
    app.blueprint(webhook_bp)

    @app.get("/")
    async def health_check(request):
        """Проверка работоспособности API"""
        return sanic_json({
            "status": "ok",
            "message": "Sanic Payment API is running",
            "version": "1.0.0"
        })
    
    @app.get("/health")
    async def health(request):
        """Health check endpoint"""
        return sanic_json({
            "status": "healthy",
            "message": "API is running",
            "version": "1.0.0"
        })
    
    return app


if __name__ == "__main__":
    app = create_app()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    # Запуск в single process режиме для отладки
    app.run(host=host, port=port, debug=debug, single_process=True)
