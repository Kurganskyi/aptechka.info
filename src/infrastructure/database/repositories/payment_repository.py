"""
Payment repository implementation
"""

from typing import Optional, List
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.domain.entities.payment import Order, Product, UserProduct, PaymentStatus
from src.domain.repositories.payment_repository import PaymentRepository
from src.infrastructure.database.models.order import OrderModel, UserProductModel
from src.infrastructure.database.models.product import ProductModel
from src.domain.exceptions import ProductNotFoundException, OrderNotFoundException


class SQLAlchemyPaymentRepository(PaymentRepository):
    """Реализация репозитория платежей через SQLAlchemy"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # Products methods
    async def get_product_by_slug(self, slug: str) -> Optional[Product]:
        """Получить продукт по slug"""
        try:
            result = await self.session.execute(
                select(ProductModel).where(ProductModel.slug == slug)
            )
            product_model = result.scalar_one_or_none()
            
            if product_model:
                return self._product_model_to_entity(product_model)
            return None
            
        except Exception as e:
            logger.error(f"Error getting product by slug {slug}: {e}")
            raise
    
    async def get_all_products(self) -> List[Product]:
        """Получить все продукты"""
        try:
            result = await self.session.execute(
                select(ProductModel).order_by(ProductModel.sort_order, ProductModel.name)
            )
            product_models = result.scalars().all()
            
            return [self._product_model_to_entity(model) for model in product_models]
            
        except Exception as e:
            logger.error(f"Error getting all products: {e}")
            raise
    
    async def get_active_products(self) -> List[Product]:
        """Получить активные продукты"""
        try:
            result = await self.session.execute(
                select(ProductModel)
                .where(ProductModel.is_active == True)
                .order_by(ProductModel.sort_order, ProductModel.name)
            )
            product_models = result.scalars().all()
            
            return [self._product_model_to_entity(model) for model in product_models]
            
        except Exception as e:
            logger.error(f"Error getting active products: {e}")
            raise
    
    # Orders methods
    async def create_order(self, order: Order) -> Order:
        """Создать заказ"""
        try:
            order_model = OrderModel(
                user_id=order.user_id,
                product_id=order.product_id,
                amount_kopecks=order.amount_kopecks,
                currency=order.currency,
                status=order.status.value,
                bepaid_transaction_id=order.bepaid_transaction_id,
                bepaid_checkout_url=order.bepaid_checkout_url,
                payment_method=order.payment_method.value if order.payment_method else None,
                expires_at=order.expires_at,
                paid_at=order.paid_at,
                created_at=order.created_at,
                updated_at=order.updated_at,
            )
            
            self.session.add(order_model)
            await self.session.flush()
            
            # Обновляем ID в entity
            order.id = order_model.id
            
            logger.info(f"Order created: {order.id} for user {order.user_id}")
            return order
            
        except Exception as e:
            logger.error(f"Error creating order for user {order.user_id}: {e}")
            raise
    
    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Получить заказ по ID"""
        try:
            result = await self.session.execute(
                select(OrderModel).where(OrderModel.id == order_id)
            )
            order_model = result.scalar_one_or_none()
            
            if order_model:
                return self._order_model_to_entity(order_model)
            return None
            
        except Exception as e:
            logger.error(f"Error getting order by id {order_id}: {e}")
            raise
    
    async def get_order_by_bepaid_id(self, bepaid_transaction_id: str) -> Optional[Order]:
        """Получить заказ по bePaid transaction ID"""
        try:
            result = await self.session.execute(
                select(OrderModel).where(OrderModel.bepaid_transaction_id == bepaid_transaction_id)
            )
            order_model = result.scalar_one_or_none()
            
            if order_model:
                return self._order_model_to_entity(order_model)
            return None
            
        except Exception as e:
            logger.error(f"Error getting order by bepaid_id {bepaid_transaction_id}: {e}")
            raise
    
    async def update_order(self, order: Order) -> Order:
        """Обновить заказ"""
        try:
            await self.session.execute(
                update(OrderModel)
                .where(OrderModel.id == order.id)
                .values(
                    status=order.status.value,
                    bepaid_transaction_id=order.bepaid_transaction_id,
                    bepaid_checkout_url=order.bepaid_checkout_url,
                    payment_method=order.payment_method.value if order.payment_method else None,
                    expires_at=order.expires_at,
                    paid_at=order.paid_at,
                    updated_at=order.updated_at,
                )
            )
            
            logger.info(f"Order updated: {order.id}")
            return order
            
        except Exception as e:
            logger.error(f"Error updating order {order.id}: {e}")
            raise
    
    async def get_user_orders(self, user_id: int) -> List[Order]:
        """Получить заказы пользователя"""
        try:
            result = await self.session.execute(
                select(OrderModel)
                .where(OrderModel.user_id == user_id)
                .order_by(OrderModel.created_at.desc())
            )
            order_models = result.scalars().all()
            
            return [self._order_model_to_entity(model) for model in order_models]
            
        except Exception as e:
            logger.error(f"Error getting user orders for {user_id}: {e}")
            raise
    
    async def get_orders_by_status(self, status: PaymentStatus) -> List[Order]:
        """Получить заказы по статусу"""
        try:
            result = await self.session.execute(
                select(OrderModel)
                .where(OrderModel.status == status.value)
                .order_by(OrderModel.created_at.desc())
            )
            order_models = result.scalars().all()
            
            return [self._order_model_to_entity(model) for model in order_models]
            
        except Exception as e:
            logger.error(f"Error getting orders by status {status}: {e}")
            raise
    
    # User Products methods
    async def create_user_product(self, user_product: UserProduct) -> UserProduct:
        """Создать покупку пользователя"""
        try:
            user_product_model = UserProductModel(
                user_id=user_product.user_id,
                product_id=user_product.product_id,
                order_id=user_product.order_id,
                purchased_at=user_product.purchased_at,
                file_delivered=user_product.file_delivered,
                delivery_attempts=user_product.delivery_attempts,
                last_delivery_attempt=user_product.last_delivery_attempt,
            )
            
            self.session.add(user_product_model)
            await self.session.flush()
            
            # Обновляем ID в entity
            user_product.id = user_product_model.id
            
            logger.info(f"User product created: {user_product.id}")
            return user_product
            
        except Exception as e:
            logger.error(f"Error creating user product: {e}")
            raise
    
    async def get_user_products(self, user_id: int) -> List[UserProduct]:
        """Получить покупки пользователя"""
        try:
            result = await self.session.execute(
                select(UserProductModel)
                .where(UserProductModel.user_id == user_id)
                .order_by(UserProductModel.purchased_at.desc())
            )
            user_product_models = result.scalars().all()
            
            return [self._user_product_model_to_entity(model) for model in user_product_models]
            
        except Exception as e:
            logger.error(f"Error getting user products for {user_id}: {e}")
            raise
    
    async def has_user_product(self, user_id: int, product_slug: str) -> bool:
        """Проверить, есть ли у пользователя продукт"""
        try:
            # Сначала получаем продукт
            product = await self.get_product_by_slug(product_slug)
            if not product:
                return False
            
            # Проверяем, есть ли у пользователя этот продукт
            result = await self.session.execute(
                select(UserProductModel.id)
                .where(
                    and_(
                        UserProductModel.user_id == user_id,
                        UserProductModel.product_id == product.id
                    )
                )
            )
            
            return result.scalar_one_or_none() is not None
            
        except Exception as e:
            logger.error(f"Error checking user product {user_id}, {product_slug}: {e}")
            raise
    
    async def get_undelivered_products(self) -> List[UserProduct]:
        """Получить не доставленные продукты"""
        try:
            result = await self.session.execute(
                select(UserProductModel)
                .where(UserProductModel.file_delivered == False)
                .order_by(UserProductModel.purchased_at.asc())
            )
            user_product_models = result.scalars().all()
            
            return [self._user_product_model_to_entity(model) for model in user_product_models]
            
        except Exception as e:
            logger.error(f"Error getting undelivered products: {e}")
            raise
    
    async def mark_as_delivered(self, user_product_id: int) -> bool:
        """Отметить как доставленный"""
        try:
            result = await self.session.execute(
                update(UserProductModel)
                .where(UserProductModel.id == user_product_id)
                .values(file_delivered=True)
            )
            
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"Error marking as delivered {user_product_id}: {e}")
            raise
    
    # Helper methods
    def _product_model_to_entity(self, model: ProductModel) -> Product:
        """Преобразование модели продукта в entity"""
        return Product(
            id=model.id,
            slug=model.slug,
            name=model.name,
            description=model.description,
            price_kopecks=model.price_kopecks,
            file_id=model.file_id,
            file_type=model.file_type,
            is_active=model.is_active,
            sort_order=model.sort_order,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def _order_model_to_entity(self, model: OrderModel) -> Order:
        """Преобразование модели заказа в entity"""
        return Order(
            id=model.id,
            user_id=model.user_id,
            product_id=model.product_id,
            amount_kopecks=model.amount_kopecks,
            currency=model.currency,
            status=PaymentStatus(model.status),
            bepaid_transaction_id=model.bepaid_transaction_id,
            bepaid_checkout_url=model.bepaid_checkout_url,
            payment_method=model.payment_method,
            expires_at=model.expires_at,
            paid_at=model.paid_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def _user_product_model_to_entity(self, model: UserProductModel) -> UserProduct:
        """Преобразование модели покупки пользователя в entity"""
        return UserProduct(
            id=model.id,
            user_id=model.user_id,
            product_id=model.product_id,
            order_id=model.order_id,
            purchased_at=model.purchased_at,
            file_delivered=model.file_delivered,
            delivery_attempts=model.delivery_attempts,
            last_delivery_attempt=model.last_delivery_attempt,
        )
