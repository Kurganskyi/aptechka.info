"""
Start command handler
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from loguru import logger

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.use_cases.user.create_or_update_user import CreateOrUpdateUserUseCase
from src.infrastructure.database.session import get_db_session
from src.infrastructure.database.repositories.user_repository import SQLAlchemyUserRepository
from src.presentation.keyboards.inline import main_menu_keyboard
from src.utils.helpers import parse_referral_start_param, format_user_display_name

router = Router()


@router.message(CommandStart())
async def start_command(message: Message):
    """Обработчик команды /start"""
    try:
        user = message.from_user
        
        # Парсинг реферального параметра
        start_param = ""
        if message.text and len(message.text.split()) > 1:
            start_param = message.text.split()[1]
        
        referral_id = parse_referral_start_param(start_param)
        
        # Создание или обновление пользователя
        async with get_db_session() as session:
            user_repository = SQLAlchemyUserRepository(session)
            create_or_update_user_uc = CreateOrUpdateUserUseCase(user_repository)
            
            db_user = await create_or_update_user_uc.execute(user)
            
            # TODO: Обработать реферальную программу если referral_id
        
        # Логирование
        display_name = format_user_display_name(
            user.first_name, 
            user.last_name, 
            user.username
        )
        
        logger.info(f"User started bot: {display_name} (ID: {user.id})")
        if referral_id:
            logger.info(f"Referral detected: {referral_id}")
        
        # Проверяем, есть ли у пользователя трипвайер
        has_tripwire = False  # TODO: Реализовать проверку через PaymentRepository
        
        # Отправка приветственного сообщения
        await message.answer(
            "👋 Добро пожаловать в бот аптечек!\n\n"
            "Здесь вы найдете:\n"
            "• Готовые комплекты аптечек для разных ситуаций\n"
            "• Подробные описания и рекомендации\n"
            "• Возможность проверить свои знания\n\n"
            "Выберите действие:",
            reply_markup=main_menu_keyboard(has_tripwire=has_tripwire)
        )
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer(
            "Произошла ошибка. Попробуйте позже или обратитесь в поддержку."
        )
