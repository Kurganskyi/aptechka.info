"""
Payment handlers
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from loguru import logger

from src.domain.entities.user import User
from src.domain.entities.payment import PaymentStatus
from src.domain.repositories.payment_repository import PaymentRepository
from src.domain.use_cases.payment.create_payment import CreatePaymentUseCase
from src.infrastructure.database.session import get_db_session
from src.infrastructure.database.repositories.payment_repository import SQLAlchemyPaymentRepository
from src.presentation.keyboards.inline import payment_keyboard, back_to_menu_keyboard
from src.utils.helpers import format_price_kopecks

router = Router()


@router.callback_query(F.data.startswith("tripwire_"))
async def handle_tripwire_payment(callback: CallbackQuery):
    """Обработка оплаты трипвайера"""
    try:
        await callback.answer()
        
        # Извлекаем тип трипвайера из callback_data
        tripwire_type = callback.data  # tripwire_1byn или tripwire_99byn
        
        # Получаем пользователя (TODO: реализовать получение из БД)
        user = User(
            id=1,  # Временное значение
            telegram_id=callback.from_user.id,
            first_name=callback.from_user.first_name,
            last_name=callback.from_user.last_name,
            username=callback.from_user.username,
        )
        
        # Создаем платеж
        async with get_db_session() as session:
            payment_repository = SQLAlchemyPaymentRepository(session)
            create_payment_uc = CreatePaymentUseCase(payment_repository)
            
            try:
                order = await create_payment_uc.execute(
                    user=user,
                    product_slug=tripwire_type,
                    user_email=None,  # TODO: получить email пользователя
                    user_phone=None   # TODO: получить телефон пользователя
                )
                
                # Отправляем ссылку для оплаты
                product_name = "Трипвайер за 1 BYN" if tripwire_type == "tripwire_1byn" else "Трипвайер за 99 BYN"
                
                await callback.message.edit_text(
                    f"💳 Оплата {product_name}\n\n"
                    f"Сумма: {format_price_kopecks(order.amount_kopecks)}\n"
                    f"Ссылка для оплаты активна 24 часа.\n\n"
                    "Нажмите кнопку ниже для перехода к оплате:",
                    reply_markup=payment_keyboard(order.bepaid_checkout_url, product_name)
                )
                
                logger.info(f"Payment link sent to user {user.telegram_id} for {tripwire_type}")
                
            except Exception as e:
                logger.error(f"Error creating payment: {e}")
                await callback.message.edit_text(
                    "❌ Произошла ошибка при создании платежа. Попробуйте позже или обратитесь в поддержку.",
                    reply_markup=back_to_menu_keyboard()
                )
        
    except Exception as e:
        logger.error(f"Error in handle_tripwire_payment: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data.startswith("kit_"))
async def handle_kit_payment(callback: CallbackQuery):
    """Обработка оплаты аптечки"""
    try:
        await callback.answer()
        
        # Извлекаем тип аптечки из callback_data
        kit_type = callback.data  # kit_family, kit_summer, kit_child, kit_vacation
        
        # Получаем пользователя (TODO: реализовать получение из БД)
        user = User(
            id=1,  # Временное значение
            telegram_id=callback.from_user.id,
            first_name=callback.from_user.first_name,
            last_name=callback.from_user.last_name,
            username=callback.from_user.username,
        )
        
        # Создаем платеж
        async with get_db_session() as session:
            payment_repository = SQLAlchemyPaymentRepository(session)
            create_payment_uc = CreatePaymentUseCase(payment_repository)
            
            try:
                order = await create_payment_uc.execute(
                    user=user,
                    product_slug=kit_type,
                    user_email=None,  # TODO: получить email пользователя
                    user_phone=None   # TODO: получить телефон пользователя
                )
                
                # Получаем информацию о продукте
                product = await payment_repository.get_product_by_slug(kit_type)
                product_name = product.name if product else kit_type
                
                await callback.message.edit_text(
                    f"💳 Оплата: {product_name}\n\n"
                    f"Сумма: {format_price_kopecks(order.amount_kopecks)}\n"
                    f"Ссылка для оплаты активна 24 часа.\n\n"
                    "Нажмите кнопку ниже для перехода к оплате:",
                    reply_markup=payment_keyboard(order.bepaid_checkout_url, product_name)
                )
                
                logger.info(f"Payment link sent to user {user.telegram_id} for {kit_type}")
                
            except Exception as e:
                logger.error(f"Error creating payment: {e}")
                await callback.message.edit_text(
                    "❌ Произошла ошибка при создании платежа. Попробуйте позже или обратитесь в поддержку.",
                    reply_markup=back_to_menu_keyboard()
                )
        
    except Exception as e:
        logger.error(f"Error in handle_kit_payment: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "get_guide")
async def handle_guide_payment(callback: CallbackQuery):
    """Обработка оплаты гайда за 1 руб"""
    try:
        await callback.answer()
        
        # Получаем пользователя (TODO: реализовать получение из БД)
        user = User(
            id=1,  # Временное значение
            telegram_id=callback.from_user.id,
            first_name=callback.from_user.first_name,
            last_name=callback.from_user.last_name,
            username=callback.from_user.username,
        )
        
        # Создаем платеж
        async with get_db_session() as session:
            payment_repository = SQLAlchemyPaymentRepository(session)
            create_payment_uc = CreatePaymentUseCase(payment_repository)
            
            try:
                order = await create_payment_uc.execute(
                    user=user,
                    product_slug="guide_1byn",
                    user_email=None,  # TODO: получить email пользователя
                    user_phone=None   # TODO: получить телефон пользователя
                )
                
                await callback.message.edit_text(
                    f"💳 Оплата: Гайд за 1 BYN\n\n"
                    f"Сумма: {format_price_kopecks(order.amount_kopecks)}\n"
                    f"Ссылка для оплаты активна 24 часа.\n\n"
                    "Нажмите кнопку ниже для перехода к оплате:",
                    reply_markup=payment_keyboard(order.bepaid_checkout_url, "Гайд за 1 BYN")
                )
                
                logger.info(f"Payment link sent to user {user.telegram_id} for guide")
                
            except Exception as e:
                logger.error(f"Error creating payment: {e}")
                await callback.message.edit_text(
                    "❌ Произошла ошибка при создании платежа. Попробуйте позже или обратитесь в поддержку.",
                    reply_markup=back_to_menu_keyboard()
                )
        
    except Exception as e:
        logger.error(f"Error in handle_guide_payment: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)
