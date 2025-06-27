"""Сервис для обработки вебхуков"""

import hashlib
from typing import Dict, Any
from decimal import Decimal

from ..services.user_service import UserService
from ..services.account_service import AccountService
from ..services.payment_service import PaymentService


class WebhookService:
    """Сервис для обработки вебхуков платежной системы"""
    
    @staticmethod
    def verify_signature(data: Dict[str, Any], secret_key: str, provided_signature: str) -> bool:
        """
        Проверка SHA256 подписи вебхука
        Формат: {account_id}{amount}{transaction_id}{user_id}{secret_key}
        """
        # Формируем строку для подписи в алфавитном порядке ключей
        signature_string = f"{data['account_id']}{data['amount']}{data['transaction_id']}{data['user_id']}{secret_key}"
        
        # Вычисляем SHA256 хеш
        calculated_signature = hashlib.sha256(signature_string.encode()).hexdigest()
        
        return calculated_signature == provided_signature
    
    @staticmethod
    async def process_payment(
        transaction_id: str,
        account_id: int,
        user_id: int,
        amount: Decimal,
        signature: str,
        secret_key: str
    ) -> Dict[str, Any]:
        """
        Обработка платежа из вебхука
        
        Возвращает словарь с результатом:
        {"success": bool, "message": str, "error_code": str}
        """
        
        # 1. Проверяем подпись
        data_dict = {
            "account_id": account_id,
            "amount": str(amount),
            "transaction_id": transaction_id,
            "user_id": user_id
        }
        
        if not WebhookService.verify_signature(data_dict, secret_key, signature):
            return {
                "success": False,
                "message": "Неверная подпись",
                "error_code": "INVALID_SIGNATURE"
            }
        
        # 2. Проверяем уникальность транзакции
        existing_payment = await PaymentService.get_payment_by_transaction_id(transaction_id)
        if existing_payment:
            return {
                "success": False,
                "message": "Транзакция уже обработана",
                "error_code": "DUPLICATE_TRANSACTION"
            }
        
        # 3. Проверяем существование пользователя
        user = await UserService.get_user_by_id(user_id)
        if not user:
            return {
                "success": False,
                "message": "Пользователь не найден",
                "error_code": "USER_NOT_FOUND"
            }
        
        # 4. Проверяем/создаем счет
        account = await AccountService.get_account_by_id(account_id)
        if not account:
            # Создаем новый счет для пользователя
            try:
                account = await AccountService.create_account(
                    user_id=user_id,
                    account_id=account_id
                )
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Ошибка создания счета: {str(e)}",
                    "error_code": "ACCOUNT_CREATION_ERROR"
                }
        else:
            # Проверяем, что счет принадлежит указанному пользователю
            if account.user_id != user_id:
                return {
                    "success": False,
                    "message": "Счет не принадлежит пользователю",
                    "error_code": "ACCOUNT_OWNERSHIP_ERROR"
                }
        
        # 5. Создаем запись о платеже
        try:
            payment = await PaymentService.create_payment(
                transaction_id=transaction_id,
                account_id=account_id,
                user_id=user_id,
                amount=amount
            )
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка создания платежа: {str(e)}",
                "error_code": "PAYMENT_CREATION_ERROR"
            }
        
        # 6. Начисляем сумму на счет пользователя
        try:
            await AccountService.add_to_balance(
                account_id=account_id,
                amount=amount
            )
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка начисления средств: {str(e)}",
                "error_code": "BALANCE_UPDATE_ERROR"
            }
        
        return {
            "success": True,
            "message": "Платеж успешно обработан",
            "payment_id": payment.id,
            "new_balance": str(account.balance + amount)
        }
