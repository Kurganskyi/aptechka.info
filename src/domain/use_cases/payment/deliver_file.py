"""
Deliver file use case
"""

from typing import Optional
from loguru import logger

from src.domain.entities.user import User
from src.domain.entities.payment import UserProduct
from src.domain.repositories.payment_repository import PaymentRepository


class DeliverFileUseCase:
    """Use case для доставки файла после оплаты"""
    
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository
    
    async def execute(self, user: User, product_slug: str) -> Optional[str]:
        """
        Доставить файл пользователю
        
        Args:
            user: Пользователь
            product_slug: Slug продукта
        
        Returns:
            file_id для отправки или None если не найден
        """
        try:
            # Проверяем, есть ли у пользователя продукт
            has_product = await self.payment_repository.has_user_product(user.id, product_slug)
            
            if not has_product:
                logger.warning(f"User {user.telegram_id} doesn't have product {product_slug}")
                return None
            
            # Получаем продукт
            product = await self.payment_repository.get_product_by_slug(product_slug)
            if not product or not product.file_id:
                logger.warning(f"Product {product_slug} not found or has no file_id")
                return None
            
            # Получаем информацию о покупке
            user_products = await self.payment_repository.get_user_products(user.id)
            user_product = next(
                (up for up in user_products if up.product_id == product.id), 
                None
            )
            
            if not user_product:
                logger.warning(f"UserProduct not found for user {user.telegram_id}, product {product_slug}")
                return None
            
            # Помечаем как доставленный
            await self.payment_repository.mark_as_delivered(user_product.id)
            
            logger.info(f"File delivered to user {user.telegram_id}: {product_slug}")
            
            return product.file_id
            
        except Exception as e:
            logger.error(f"Error delivering file to user {user.telegram_id}: {e}")
            return None
