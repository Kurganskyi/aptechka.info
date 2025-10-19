"""
Process payment use case
"""

from typing import Optional
from datetime import datetime
from loguru import logger

from src.domain.entities.payment import Order, UserProduct, PaymentStatus, PaymentMethod
from src.domain.repositories.payment_repository import PaymentRepository
from src.infrastructure.payment.bepaid_client import bepaid_client
from src.domain.exceptions import OrderNotFoundException, PaymentException


class ProcessPaymentUseCase:
    """Use case для обработки платежа"""
    
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository
    
    async def execute(self, transaction_id: str) -> Optional[Order]:
        """
        Обработать платеж по transaction_id
        
        Args:
            transaction_id: ID транзакции от bePaid
        
        Returns:
            Обновленный заказ или None если не найден
        """
        try:
            # Получаем заказ по transaction_id
            order = await self.payment_repository.get_order_by_bepaid_id(transaction_id)
            if not order:
                logger.warning(f"Order not found for transaction_id: {transaction_id}")
                return None
            
            # Проверяем статус в bePaid
            try:
                payment_status = await bepaid_client.get_payment_status(transaction_id)
                logger.info(f"Payment status from bePaid: {payment_status}")
                
                # Обновляем статус заказа в зависимости от ответа bePaid
                if self._is_payment_successful(payment_status):
                    await self._mark_payment_as_successful(order, payment_status)
                elif self._is_payment_failed(payment_status):
                    await self._mark_payment_as_failed(order)
                
                return order
                
            except Exception as e:
                logger.error(f"Failed to get payment status from bePaid: {e}")
                # Помечаем заказ как неудачный
                await self._mark_payment_as_failed(order)
                return order
            
        except Exception as e:
            logger.error(f"Error processing payment {transaction_id}: {e}")
            raise PaymentException(f"Error processing payment: {e}")
    
    async def _mark_payment_as_successful(self, order: Order, payment_status: dict):
        """Отметить платеж как успешный"""
        try:
            # Обновляем статус заказа
            order.status = PaymentStatus.PAID
            order.paid_at = datetime.utcnow()
            
            # Определяем способ оплаты из ответа bePaid
            payment_method = self._extract_payment_method(payment_status)
            if payment_method:
                order.payment_method = payment_method
            
            await self.payment_repository.update_order(order)
            
            # Создаем запись о покупке пользователя
            user_product = UserProduct(
                id=0,
                user_id=order.user_id,
                product_id=order.product_id,
                order_id=order.id,
                purchased_at=datetime.utcnow(),
                file_delivered=False,
            )
            
            await self.payment_repository.create_user_product(user_product)
            
            logger.info(f"Payment marked as successful: order_id={order.id}")
            
        except Exception as e:
            logger.error(f"Failed to mark payment as successful: {e}")
            raise
    
    async def _mark_payment_as_failed(self, order: Order):
        """Отметить платеж как неудачный"""
        try:
            order.status = PaymentStatus.FAILED
            await self.payment_repository.update_order(order)
            
            logger.info(f"Payment marked as failed: order_id={order.id}")
            
        except Exception as e:
            logger.error(f"Failed to mark payment as failed: {e}")
            raise
    
    def _is_payment_successful(self, payment_status: dict) -> bool:
        """Проверить, успешен ли платеж"""
        # Логика определения успешности платежа на основе ответа bePaid
        # Это зависит от структуры ответа API bePaid
        if "transaction" in payment_status:
            transaction = payment_status["transaction"]
            status = transaction.get("status", "").lower()
            return status in ["successful", "success", "completed"]
        
        return False
    
    def _is_payment_failed(self, payment_status: dict) -> bool:
        """Проверить, неудачен ли платеж"""
        if "transaction" in payment_status:
            transaction = payment_status["transaction"]
            status = transaction.get("status", "").lower()
            return status in ["failed", "error", "declined", "cancelled"]
        
        return False
    
    def _extract_payment_method(self, payment_status: dict) -> Optional[PaymentMethod]:
        """Извлечь способ оплаты из ответа bePaid"""
        try:
            if "transaction" in payment_status:
                transaction = payment_status["transaction"]
                payment_method = transaction.get("payment_method", "").lower()
                
                if "card" in payment_method:
                    return PaymentMethod.CARD
                elif "erip" in payment_method:
                    return PaymentMethod.ERIP
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting payment method: {e}")
            return None
