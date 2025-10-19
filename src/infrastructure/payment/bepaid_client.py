"""
bePaid API client
"""

import json
from typing import Dict, Any, Optional
from aiohttp import ClientSession
from loguru import logger

from src.config.settings import settings


class BePaidClient:
    """Клиент для работы с bePaid API"""
    
    def __init__(self):
        self.shop_id = settings.bepaid_shop_id
        self.secret_key = settings.bepaid_secret_key
        self.api_url = settings.bepaid_api_url
        self.webhook_url = f"{settings.webhook_host}/webhook/bepaid"
    
    async def create_payment(
        self,
        amount: int,  # в копейках
        currency: str = "BYN",
        description: str = "",
        order_id: str = "",
        user_email: Optional[str] = None,
        user_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Создание платежа
        
        Args:
            amount: Сумма в копейках
            currency: Валюта (BYN)
            description: Описание платежа
            order_id: ID заказа
            user_email: Email пользователя
            user_phone: Телефон пользователя
        
        Returns:
            Ответ от bePaid API
        """
        try:
            # Подготовка данных для запроса
            payment_data = {
                "request": {
                    "amount": amount,
                    "currency": currency,
                    "description": description,
                    "order_id": order_id,
                    "tracking_id": order_id,
                    "notification_url": self.webhook_url,
                    "success_url": f"https://t.me/{settings.bot_token.split(':')[0]}",
                    "fail_url": f"https://t.me/{settings.bot_token.split(':')[0]}",
                    "test": not settings.is_production,
                }
            }
            
            # Добавление данных пользователя если есть
            if user_email or user_phone:
                payment_data["request"]["customer"] = {}
                if user_email:
                    payment_data["request"]["customer"]["email"] = user_email
                if user_phone:
                    payment_data["request"]["customer"]["phone"] = user_phone
            
            logger.info(f"Creating payment: {payment_data}")
            
            # Отправка запроса
            async with ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/beyag/payments",
                    json=payment_data,
                    auth=(self.shop_id, self.secret_key),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 201:
                        result = await response.json()
                        logger.info(f"Payment created successfully: {result}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to create payment: {response.status} - {error_text}")
                        raise Exception(f"bePaid API error: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            raise
    
    async def get_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        Получение статуса платежа
        
        Args:
            transaction_id: ID транзакции
        
        Returns:
            Статус платежа
        """
        try:
            async with ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/beyag/payments/{transaction_id}",
                    auth=(self.shop_id, self.secret_key)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Payment status: {result}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get payment status: {response.status} - {error_text}")
                        raise Exception(f"bePaid API error: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"Error getting payment status: {e}")
            raise
    
    def get_payment_url(self, checkout_response: Dict[str, Any]) -> Optional[str]:
        """
        Извлечение URL для оплаты из ответа bePaid
        
        Args:
            checkout_response: Ответ от bePaid при создании платежа
        
        Returns:
            URL для оплаты или None
        """
        try:
            if "checkout" in checkout_response:
                checkout = checkout_response["checkout"]
                if "redirect_url" in checkout:
                    return checkout["redirect_url"]
            
            logger.warning(f"No payment URL found in response: {checkout_response}")
            return None
        
        except Exception as e:
            logger.error(f"Error extracting payment URL: {e}")
            return None
    
    def get_transaction_id(self, checkout_response: Dict[str, Any]) -> Optional[str]:
        """
        Извлечение ID транзакции из ответа bePaid
        
        Args:
            checkout_response: Ответ от bePaid при создании платежа
        
        Returns:
            ID транзакции или None
        """
        try:
            if "checkout" in checkout_response:
                checkout = checkout_response["checkout"]
                if "token" in checkout:
                    return checkout["token"]
            
            logger.warning(f"No transaction ID found in response: {checkout_response}")
            return None
        
        except Exception as e:
            logger.error(f"Error extracting transaction ID: {e}")
            return None


# Глобальный экземпляр
bepaid_client = BePaidClient()
