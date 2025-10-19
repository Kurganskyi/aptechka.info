"""
FAQ handlers
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.domain.entities.user import User
from src.domain.repositories.payment_repository import PaymentRepository
from src.infrastructure.database.session import get_db_session
from src.infrastructure.database.repositories.payment_repository import SQLAlchemyPaymentRepository
from src.presentation.keyboards.inline import (
    faq_response_keyboard,
    back_to_menu_keyboard,
    main_menu_keyboard
)
from src.presentation.states import FAQStates
from src.utils.helpers import is_admin_user
from src.config.settings import settings

router = Router()

# FAQ ответы
FAQ_ANSWERS = {
    "faq_where_buy": {
        "answer": "В нашем каталоге подберем доступные препараты, которые есть в любой аптеке. Как происходит менеджер по приобретению. Если лекарств с разными рецептами хранения. Пакет для анализа - если чего-то нет в наличии.",
        "tripwire_check": True
    },
    "faq_relevance": {
        "answer": "В следующем смогу на вопросы приоритизации по мы не исследуем на эффект задержки, поэтому у каждой аптеки выбраны только лучшие препараты для организации хранения лекарств.",
        "tripwire_check": True
    },
    "faq_price": {
        "answer": "Стоимость лекарств зависит от выбранной аптечки. Мы подбираем препараты разных ценовых категорий для оптимального соотношения цена/качество.",
        "tripwire_check": True
    },
    "faq_looks": {
        "answer": "Каждая аптечка включает подробное описание с фотографиями, список препаратов с инструкциями по применению и рекомендации по хранению.",
        "tripwire_check": True
    }
}


@router.callback_query(F.data.startswith("faq_"))
async def handle_faq_question(callback: CallbackQuery, state: FSMContext, user: User):
    """Обработка FAQ вопросов"""
    try:
        await callback.answer()
        
        faq_type = callback.data
        
        if faq_type == "faq_custom":
            # Переход к пользовательскому вопросу
            await state.set_state(FAQStates.waiting_for_question)
            await callback.message.edit_text(
                "❓ Свой вопрос\n\n"
                "Напишите ваш вопрос, и мы обязательно ответим!",
                reply_markup=back_to_menu_keyboard()
            )
            return
        
        # Получаем ответ на FAQ
        if faq_type not in FAQ_ANSWERS:
            await callback.answer("Вопрос не найден", show_alert=True)
            return
        
        faq_data = FAQ_ANSWERS[faq_type]
        answer = faq_data["answer"]
        tripwire_check = faq_data["tripwire_check"]
        
        await callback.message.edit_text(
            f"❓ Ответ на ваш вопрос:\n\n{answer}",
            reply_markup=faq_response_keyboard()
        )
        
        # Сохраняем информацию для проверки трипвайера
        await state.update_data(
            faq_answered=True,
            tripwire_check_required=tripwire_check
        )
        
        logger.info(f"FAQ answered for user {user.telegram_id}: {faq_type}")
        
    except Exception as e:
        logger.error(f"Error handling FAQ question: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "faq_great")
async def faq_great_response(callback: CallbackQuery, state: FSMContext, user: User):
    """Ответ 'Отлично!' на FAQ"""
    try:
        await callback.answer()
        
        # Проверяем, нужна ли проверка трипвайера
        data = await state.get_data()
        tripwire_check_required = data.get("tripwire_check_required", False)
        
        if tripwire_check_required:
            # Проверяем, есть ли у пользователя трипвайер
            async with get_db_session() as session:
                payment_repository = SQLAlchemyPaymentRepository(session)
                has_tripwire = await payment_repository.has_user_product(user.id, "tripwire_1byn")
            
            # Возвращаем в соответствующее меню
            await callback.message.edit_text(
                "👍 Отлично! Рады, что смогли помочь!",
                reply_markup=main_menu_keyboard(has_tripwire=not has_tripwire)
            )
        else:
            await callback.message.edit_text(
                "👍 Отлично! Рады, что смогли помочь!",
                reply_markup=main_menu_keyboard(has_tripwire=True)
            )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in faq_great_response: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "faq_another")
async def faq_another_question(callback: CallbackQuery, state: FSMContext):
    """Запрос другого вопроса"""
    try:
        await callback.answer()
        
        await callback.message.edit_text(
            "❓ Часто задаваемые вопросы\n\n"
            "Выберите вопрос:",
            reply_markup=faq_keyboard()
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in faq_another_question: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.message(FAQStates.waiting_for_question)
async def handle_custom_question(message: Message, state: FSMContext, user: User):
    """Обработка пользовательского вопроса"""
    try:
        question_text = message.text
        
        if not question_text or len(question_text.strip()) < 10:
            await message.answer(
                "❌ Вопрос слишком короткий. Пожалуйста, напишите более подробный вопрос (минимум 10 символов)."
            )
            return
        
        # TODO: Сохранить вопрос в БД через UserQuestionRepository
        # Пока просто логируем
        logger.info(f"Custom question from user {user.telegram_id}: {question_text}")
        
        await message.answer(
            "✅ Спасибо за обращение! Мы получили ваш вопрос и обязательно ответим в ближайшее время.\n\n"
            "Обычно мы отвечаем в течение 24 часов.",
            reply_markup=back_to_menu_keyboard()
        )
        
        await state.clear()
        
        # TODO: Уведомить админов о новом вопросе
        
    except Exception as e:
        logger.error(f"Error handling custom question: {e}")
        await message.answer("Произошла ошибка при обработке вопроса. Попробуйте позже.")
        await state.clear()
