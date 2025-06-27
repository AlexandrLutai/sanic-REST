"""Роуты для обработки вебхуков"""

from sanic import Blueprint
from sanic.response import json as sanic_json
from sanic.request import Request

from app.schemas.webhook import WebhookRequest, WebhookResponse
from app.services.webhook_service import WebhookService

webhook_bp = Blueprint("webhook", url_prefix="/api/v1/webhook")


@webhook_bp.post("/payment")
async def process_payment_webhook(request: Request):
    """Обработка вебхука от платежной системы"""
    try:
        
        webhook_data = WebhookRequest(**request.json)
        
       
        secret_key = request.app.config.get("WEBHOOK_SECRET")
        if not secret_key:
            return sanic_json(
                {"error": "Секретный ключ не настроен"}, 
                status=500
            )
        
        # Обрабатываем платеж через сервис
        result = await WebhookService.process_payment(
            transaction_id=webhook_data.transaction_id,
            account_id=webhook_data.account_id,
            user_id=webhook_data.user_id,
            amount=webhook_data.amount,
            signature=webhook_data.signature,
            secret_key=secret_key
        )
        
        if not result["success"]:
            # Определяем статус кода на основе типа ошибки
            status_codes = {
                "INVALID_SIGNATURE": 400,
                "DUPLICATE_TRANSACTION": 409,
                "USER_NOT_FOUND": 404,
                "ACCOUNT_OWNERSHIP_ERROR": 400,
                "ACCOUNT_CREATION_ERROR": 500,
                "PAYMENT_CREATION_ERROR": 500,
                "BALANCE_UPDATE_ERROR": 500
            }
            status_code = status_codes.get(result.get("error_code"), 400)
            
            return sanic_json(
                {"error": result["message"]}, 
                status=status_code
            )
        
        
        response = WebhookResponse(
            success=True,
            message=result["message"],
            transaction_id=webhook_data.transaction_id
        )
        
        return sanic_json(response.model_dump(), status=200)
        
    except ValueError as e:
        return sanic_json(
            {"error": f"Ошибка валидации: {str(e)}"}, 
            status=400
        )
    except Exception as e:
        return sanic_json(
            {"error": f"Внутренняя ошибка сервера: {str(e)}"}, 
            status=500
        )
