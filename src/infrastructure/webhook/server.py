"""
aiohttp webhook server for bePaid
"""

import json
from typing import Dict, Any
from aiohttp import web, ClientSession
from loguru import logger

from src.config.settings import settings


class WebhookServer:
    """Webhook сервер для обработки уведомлений от bePaid"""
    
    def __init__(self):
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        """Настройка маршрутов"""
        self.app.router.add_post("/webhook/bepaid", self.handle_bepaid_webhook)
        self.app.router.add_get("/health", self.health_check)
    
    async def handle_bepaid_webhook(self, request: web.Request) -> web.Response:
        """Обработка webhook от bePaid"""
        try:
            # Получение данных
            data = await request.json()
            logger.info(f"Received bePaid webhook: {data}")
            
            # Валидация подписи (TODO: реализовать)
            # if not self._verify_signature(request, data):
            #     logger.warning("Invalid webhook signature")
            #     return web.Response(status=400, text="Invalid signature")
            
            # Обработка события
            await self._process_webhook_event(data)
            
            return web.Response(status=200, text="OK")
            
        except Exception as e:
            logger.error(f"Error processing bePaid webhook: {e}")
            return web.Response(status=500, text="Internal Server Error")
    
    async def _process_webhook_event(self, data: Dict[str, Any]):
        """Обработка события webhook"""
        event_type = data.get("event_type")
        
        if event_type == "payment_successful":
            await self._handle_payment_success(data)
        elif event_type == "payment_failed":
            await self._handle_payment_failed(data)
        else:
            logger.warning(f"Unknown webhook event type: {event_type}")
    
    async def _handle_payment_success(self, data: Dict[str, Any]):
        """Обработка успешного платежа"""
        transaction_id = data.get("transaction_id")
        logger.info(f"Payment successful: {transaction_id}")
        
        try:
            # Получаем use case для обработки платежа
            from src.utils.di import container
            from src.domain.repositories.payment_repository import PaymentRepository
            from src.domain.use_cases.payment.process_payment import ProcessPaymentUseCase
            
            # Создаем сессию БД
            from src.infrastructure.database.session import get_db_session
            async with get_db_session() as session:
                # Создаем репозиторий и use case
                payment_repository = SQLAlchemyPaymentRepository(session)
                process_payment_uc = ProcessPaymentUseCase(payment_repository)
                
                # Обрабатываем платеж
                order = await process_payment_uc.execute(transaction_id)
                
                if order and order.status == PaymentStatus.PAID:
                    logger.info(f"Payment processed successfully: order_id={order.id}")
                    # TODO: Отправить файл пользователю
                    # TODO: Уведомить админов
                else:
                    logger.warning(f"Payment processing failed: order_id={order.id if order else 'None'}")
        
        except Exception as e:
            logger.error(f"Error handling payment success: {e}")
    
    async def _handle_payment_failed(self, data: Dict[str, Any]):
        """Обработка неудачного платежа"""
        transaction_id = data.get("transaction_id")
        logger.info(f"Payment failed: {transaction_id}")
        
        try:
            # Получаем use case для обработки платежа
            from src.domain.repositories.payment_repository import PaymentRepository
            from src.domain.use_cases.payment.process_payment import ProcessPaymentUseCase
            
            # Создаем сессию БД
            from src.infrastructure.database.session import get_db_session
            async with get_db_session() as session:
                # Создаем репозиторий и use case
                payment_repository = SQLAlchemyPaymentRepository(session)
                process_payment_uc = ProcessPaymentUseCase(payment_repository)
                
                # Обрабатываем неудачный платеж
                order = await process_payment_uc.execute(transaction_id)
                
                if order and order.status == PaymentStatus.FAILED:
                    logger.info(f"Payment marked as failed: order_id={order.id}")
                    # TODO: Уведомить пользователя о неудачной оплате
        
        except Exception as e:
            logger.error(f"Error handling payment failure: {e}")
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.Response(
            status=200,
            text=json.dumps({"status": "healthy", "service": "webhook"}),
            content_type="application/json"
        )
    
    async def start(self, host: str = "0.0.0.0", port: int = 8080):
        """Запуск webhook сервера"""
        logger.info(f"Starting webhook server on {host}:{port}")
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info("Webhook server started successfully")
        return runner


# Глобальный экземпляр
webhook_server = WebhookServer()
