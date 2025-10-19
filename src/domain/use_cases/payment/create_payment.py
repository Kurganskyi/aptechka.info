"""
Create payment use case
"""

from typing import Optional
from datetime import datetime, timedelta
from loguru import logger

from src.domain.entities.payment import Order, Product, PaymentStatus
from src.domain.entities.user import User
from src.domain.repositories.payment_repository import PaymentRepository
from src.infrastructure.payment.bepaid_client import bepaid_client
from src.domain.exceptions import ProductNotFoundException, PaymentException


class CreatePaymentUseCase:
    """Use case для создания платежа"""
    
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository
    
    async def execute(
        self,
        user: User,
        product_slug: str,
        user_email: Optional[str] = None,
        user_phone: Optional[str] = None
    ) -> Order:
        """
        Создать платеж
        
        Args:
            user: Пользователь
            product_slug: Slug продукта
            user_email: Email пользователя (опционально)
            user_phone: Телефон пользователя (опционально)
        
        Returns:
            Созданный заказ с URL для оплаты
        """
        try:
            # Получаем продукт
            product = await self.payment_repository.get_product_by_slug(product_slug)
            if not product:
                raise ProductNotFoundException(f"Product with slug '{product_slug}' not found")
            
            if not product.is_available():
                raise PaymentException("Product is not available")
            
            # Проверяем, не покупал ли пользователь уже этот продукт
            has_product = await self.payment_repository.has_user_product(user.id, product_slug)
            if has_product:
                raise PaymentException("User already owns this product")
            
            # Создаем заказ
            order = Order(
                id=0,  # Будет установлен после сохранения
                user_id=user.id,
                product_id=product.id,
                amount_kopecks=product.price_kopecks,
                currency="BYN",
                status=PaymentStatus.PENDING,
                expires_at=datetime.utcnow() + timedelta(hours=24),  # 24 часа на оплату
            )
            
            # Сохраняем заказ в БД
            order = await self.payment_repository.create_order(order)
            
            # Создаем платеж в bePaid
            try:
                bepaid_response = await bepaid_client.create_payment(
                    amount=product.price_kopecks,
                    currency="BYN",
                    description=f"Оплата: {product.name}",
                    order_id=str(order.id),
                    user_email=user_email,
                    user_phone=user_phone
                )
                
                # Извлекаем данные из ответа bePaid
                payment_url = bepaid_client.get_payment_url(bepaid_response)
                transaction_id = bepaid_client.get_transaction_id(bepaid_response)
                
                if not payment_url or not transaction_id:
                    raise PaymentException("Failed to get payment URL or transaction ID from bePaid")
                
                # Обновляем заказ с данными от bePaid
                order.bepaid_transaction_id = transaction_id
                order.bepaid_checkout_url = payment_url
                order = await self.payment_repository.update_order(order)
                
                logger.info(f"Payment created successfully: order_id={order.id}, transaction_id={transaction_id}")
                return order
                
            except Exception as e:
                logger.error(f"Failed to create payment in bePaid: {e}")
                # Помечаем заказ как неудачный
                order.status = PaymentStatus.FAILED
                await self.payment_repository.update_order(order)
                raise PaymentException(f"Failed to create payment: {e}")
            
        except (ProductNotFoundException, PaymentException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in CreatePaymentUseCase: {e}")
            raise PaymentException(f"Unexpected error: {e}")
