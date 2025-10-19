"""
User repository implementation
"""

from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models.user import UserModel
from src.domain.exceptions import UserNotFoundException


class SQLAlchemyUserRepository(UserRepository):
    """Реализация репозитория пользователей через SQLAlchemy"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        try:
            result = await self.session.execute(
                select(UserModel).where(UserModel.telegram_id == telegram_id)
            )
            user_model = result.scalar_one_or_none()
            
            if user_model:
                return self._model_to_entity(user_model)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by telegram_id {telegram_id}: {e}")
            raise
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        try:
            result = await self.session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_model = result.scalar_one_or_none()
            
            if user_model:
                return self._model_to_entity(user_model)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by id {user_id}: {e}")
            raise
    
    async def create(self, user: User) -> User:
        """Создать пользователя"""
        try:
            user_model = UserModel(
                telegram_id=user.telegram_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code,
                is_blocked=user.is_blocked,
                is_admin=user.is_admin,
                referrer_id=user.referrer_id,
                last_activity_at=user.last_activity_at,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            
            self.session.add(user_model)
            await self.session.flush()
            
            # Обновляем ID в entity
            user.id = user_model.id
            
            logger.info(f"User created: {user.telegram_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user {user.telegram_id}: {e}")
            raise
    
    async def update(self, user: User) -> User:
        """Обновить пользователя"""
        try:
            await self.session.execute(
                update(UserModel)
                .where(UserModel.id == user.id)
                .values(
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    language_code=user.language_code,
                    is_blocked=user.is_blocked,
                    is_admin=user.is_admin,
                    referrer_id=user.referrer_id,
                    last_activity_at=user.last_activity_at,
                    updated_at=user.updated_at,
                )
            )
            
            logger.info(f"User updated: {user.telegram_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user {user.telegram_id}: {e}")
            raise
    
    async def get_admins(self) -> List[User]:
        """Получить список администраторов"""
        try:
            result = await self.session.execute(
                select(UserModel).where(UserModel.is_admin == True)
            )
            user_models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in user_models]
            
        except Exception as e:
            logger.error(f"Error getting admins: {e}")
            raise
    
    async def get_active_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Получить активных пользователей"""
        try:
            result = await self.session.execute(
                select(UserModel)
                .where(UserModel.is_blocked == False)
                .order_by(UserModel.last_activity_at.desc())
                .limit(limit)
                .offset(offset)
            )
            user_models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in user_models]
            
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            raise
    
    async def get_users_count(self) -> int:
        """Получить количество пользователей"""
        try:
            result = await self.session.execute(
                select(UserModel.id).count()
            )
            return result.scalar() or 0
            
        except Exception as e:
            logger.error(f"Error getting users count: {e}")
            raise
    
    async def block_user(self, user_id: int) -> bool:
        """Заблокировать пользователя"""
        try:
            result = await self.session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(is_blocked=True)
            )
            
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"Error blocking user {user_id}: {e}")
            raise
    
    async def unblock_user(self, user_id: int) -> bool:
        """Разблокировать пользователя"""
        try:
            result = await self.session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(is_blocked=False)
            )
            
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"Error unblocking user {user_id}: {e}")
            raise
    
    def _model_to_entity(self, model: UserModel) -> User:
        """Преобразование модели в entity"""
        return User(
            id=model.id,
            telegram_id=model.telegram_id,
            username=model.username,
            first_name=model.first_name,
            last_name=model.last_name,
            language_code=model.language_code,
            is_blocked=model.is_blocked,
            is_admin=model.is_admin,
            referrer_id=model.referrer_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_activity_at=model.last_activity_at,
        )
