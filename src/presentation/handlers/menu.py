"""
Menu handlers
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from loguru import logger

from src.presentation.keyboards.inline import (
    main_menu_keyboard,
    kits_menu_keyboard,
    about_me_keyboard,
    faq_keyboard,
    back_to_menu_keyboard
)
from src.config.settings import settings

router = Router()


@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    try:
        await callback.answer()
        
        # Проверяем, есть ли у пользователя трипвайер
        has_tripwire = False  # TODO: Реализовать проверку через PaymentRepository
        
        await callback.message.edit_text(
            "🏠 Главное меню\n\n"
            "Выберите действие:",
            reply_markup=main_menu_keyboard(has_tripwire=has_tripwire)
        )
        
    except Exception as e:
        logger.error(f"Error in back_to_main_menu: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "view_kits")
async def view_kits(callback: CallbackQuery):
    """Просмотр вариантов аптечек"""
    try:
        await callback.answer()
        
        await callback.message.edit_text(
            "📦 Варианты аптечек\n\n"
            "Выберите тип аптечки:",
            reply_markup=kits_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in view_kits: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "about_me")
async def about_me(callback: CallbackQuery):
    """Информация обо мне"""
    try:
        await callback.answer()
        
        await callback.message.edit_text(
            "👤 Обо мне\n\n"
            "Привет! Я создатель этого бота и эксперт по аптечкам.\n\n"
            "Моя миссия - помочь вам подготовиться к любым ситуациям "
            "с помощью правильно собранных аптечек.\n\n"
            "Выберите действие:",
            reply_markup=about_me_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in about_me: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "reviews")
async def reviews(callback: CallbackQuery):
    """Переход к отзывам"""
    try:
        await callback.answer()
        
        await callback.message.edit_text(
            "⭐ Отзывы\n\n"
            "Читайте отзывы наших клиентов и делитесь своими впечатлениями!",
            reply_markup=back_to_menu_keyboard()
        )
        
        # Отправляем ссылку на чат с отзывами
        await callback.message.answer(
            f"💬 Перейти в чат с отзывами: {settings.reviews_chat_url}",
            reply_markup=back_to_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in reviews: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "faq")
async def faq(callback: CallbackQuery):
    """FAQ"""
    try:
        await callback.answer()
        
        await callback.message.edit_text(
            "❓ Часто задаваемые вопросы\n\n"
            "Выберите вопрос:",
            reply_markup=faq_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in faq: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "test_knowledge")
async def test_knowledge(callback: CallbackQuery):
    """Проверить знания"""
    try:
        await callback.answer()
        
        await callback.message.edit_text(
            "🧠 Проверить знания!\n\n"
            "Пройдите тест из 6 каверзных вопросов и проверьте свои знания об аптечках!",
            reply_markup=back_to_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in test_knowledge: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "take_test")
async def take_test(callback: CallbackQuery):
    """Пройти тест"""
    try:
        await callback.answer()
        
        await callback.message.edit_text(
            "🧠 Пройти тест!\n\n"
            "Пройдите тест из 6 каверзных вопросов и проверьте свои знания об аптечках!",
            reply_markup=back_to_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in take_test: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)
