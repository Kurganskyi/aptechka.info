"""
Post-payment handlers - доступ к контенту после оплаты
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from loguru import logger

from src.domain.entities.user import User
from src.domain.repositories.payment_repository import PaymentRepository
from src.domain.use_cases.payment.deliver_file import DeliverFileUseCase
from src.infrastructure.database.session import get_db_session
from src.infrastructure.database.repositories.payment_repository import SQLAlchemyPaymentRepository
from src.presentation.keyboards.inline import back_to_menu_keyboard

router = Router()


@router.callback_query(F.data == "download_tripwire")
async def download_tripwire(callback: CallbackQuery, user: User):
    """Скачать трипвайер"""
    try:
        await callback.answer()
        
        async with get_db_session() as session:
            payment_repository = SQLAlchemyPaymentRepository(session)
            deliver_file_uc = DeliverFileUseCase(payment_repository)
            
            # Проверяем, какой трипвайер есть у пользователя
            has_tripwire_1byn = await payment_repository.has_user_product(user.id, "tripwire_1byn")
            has_tripwire_99byn = await payment_repository.has_user_product(user.id, "tripwire_99byn")
            
            if has_tripwire_99byn:
                file_id = await deliver_file_uc.execute(user, "tripwire_99byn")
                product_name = "Трипвайер за 99 BYN"
            elif has_tripwire_1byn:
                file_id = await deliver_file_uc.execute(user, "tripwire_1byn")
                product_name = "Трипвайер за 1 BYN"
            else:
                await callback.message.answer(
                    "❌ У вас нет доступа к трипвайеру. Сначала приобретите его.",
                    reply_markup=back_to_menu_keyboard()
                )
                return
            
            if file_id:
                await callback.message.answer(
                    f"🎥 {product_name}\n\n"
                    "Ваш файл готов к скачиванию:",
                    reply_markup=back_to_menu_keyboard()
                )
                
                # Отправляем файл
                await callback.message.answer_document(
                    document=file_id,
                    caption=f"✅ {product_name} - Спасибо за покупку!"
                )
                
                logger.info(f"Tripwire delivered to user {user.telegram_id}")
            else:
                await callback.message.answer(
                    "❌ Ошибка при получении файла. Обратитесь в поддержку.",
                    reply_markup=back_to_menu_keyboard()
                )
        
    except Exception as e:
        logger.error(f"Error downloading tripwire: {e}")
        await callback.answer("Произошла ошибка при скачивании", show_alert=True)


@router.callback_query(F.data == "download_guide")
async def download_guide(callback: CallbackQuery, user: User):
    """Скачать гайд"""
    try:
        await callback.answer()
        
        async with get_db_session() as session:
            payment_repository = SQLAlchemyPaymentRepository(session)
            deliver_file_uc = DeliverFileUseCase(payment_repository)
            
            file_id = await deliver_file_uc.execute(user, "guide_1byn")
            
            if file_id:
                await callback.message.answer(
                    "📖 Гайд за 1 BYN\n\n"
                    "Ваш файл готов к скачиванию:",
                    reply_markup=back_to_menu_keyboard()
                )
                
                # Отправляем файл
                await callback.message.answer_document(
                    document=file_id,
                    caption="✅ Гайд за 1 BYN - Спасибо за покупку!"
                )
                
                logger.info(f"Guide delivered to user {user.telegram_id}")
            else:
                await callback.message.answer(
                    "❌ У вас нет доступа к гайду. Сначала приобретите его.",
                    reply_markup=back_to_menu_keyboard()
                )
        
    except Exception as e:
        logger.error(f"Error downloading guide: {e}")
        await callback.answer("Произошла ошибка при скачивании", show_alert=True)


@router.callback_query(F.data.startswith("download_kit_"))
async def download_kit(callback: CallbackQuery, user: User):
    """Скачать аптечку"""
    try:
        await callback.answer()
        
        # Извлекаем тип аптечки
        kit_type = callback.data.replace("download_kit_", "")
        
        async with get_db_session() as session:
            payment_repository = SQLAlchemyPaymentRepository(session)
            deliver_file_uc = DeliverFileUseCase(payment_repository)
            
            file_id = await deliver_file_uc.execute(user, kit_type)
            
            if file_id:
                # Получаем информацию о продукте
                product = await payment_repository.get_product_by_slug(kit_type)
                product_name = product.name if product else kit_type
                
                await callback.message.answer(
                    f"📦 {product_name}\n\n"
                    "Ваш файл готов к скачиванию:",
                    reply_markup=back_to_menu_keyboard()
                )
                
                # Отправляем файл
                await callback.message.answer_document(
                    document=file_id,
                    caption=f"✅ {product_name} - Спасибо за покупку!"
                )
                
                logger.info(f"Kit {kit_type} delivered to user {user.telegram_id}")
            else:
                await callback.message.answer(
                    f"❌ У вас нет доступа к {kit_type}. Сначала приобретите его.",
                    reply_markup=back_to_menu_keyboard()
                )
        
    except Exception as e:
        logger.error(f"Error downloading kit {kit_type}: {e}")
        await callback.answer("Произошла ошибка при скачивании", show_alert=True)


@router.callback_query(F.data == "my_purchases")
async def show_my_purchases(callback: CallbackQuery, user: User):
    """Показать мои покупки"""
    try:
        await callback.answer()
        
        async with get_db_session() as session:
            payment_repository = SQLAlchemyPaymentRepository(session)
            
            # Получаем покупки пользователя
            user_products = await payment_repository.get_user_products(user.id)
            
            if not user_products:
                await callback.message.answer(
                    "📦 Мои покупки\n\n"
                    "У вас пока нет покупок. Выберите подходящий продукт в главном меню!",
                    reply_markup=back_to_menu_keyboard()
                )
                return
            
            # Формируем список покупок
            purchases_text = "📦 Мои покупки:\n\n"
            
            for user_product in user_products:
                product = await payment_repository.get_product_by_slug(
                    f"product_{user_product.product_id}"  # TODO: Получить slug продукта
                )
                product_name = product.name if product else f"Продукт {user_product.product_id}"
                
                status = "✅ Доставлен" if user_product.file_delivered else "📥 В обработке"
                purchases_text += f"• {product_name} - {status}\n"
            
            await callback.message.answer(
                purchases_text,
                reply_markup=back_to_menu_keyboard()
            )
        
    except Exception as e:
        logger.error(f"Error showing purchases: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)
