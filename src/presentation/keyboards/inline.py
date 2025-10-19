"""
Inline keyboards
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional


def create_inline_keyboard(
    buttons: List[List[dict]], 
    row_width: int = 2
) -> InlineKeyboardMarkup:
    """
    Создание inline клавиатуры
    
    Args:
        buttons: Список списков кнопок, где каждая кнопка - dict с 'text' и 'callback_data'
        row_width: Количество кнопок в ряду
    
    Returns:
        InlineKeyboardMarkup
    """
    keyboard = []
    
    for row in buttons:
        keyboard_row = []
        for button_data in row:
            button = InlineKeyboardButton(
                text=button_data["text"],
                callback_data=button_data["callback_data"]
            )
            keyboard_row.append(button)
        keyboard.append(keyboard_row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def main_menu_keyboard(has_tripwire: bool = True) -> InlineKeyboardMarkup:
    """Главное меню бота"""
    if has_tripwire:
        buttons = [
            [
                {"text": "💳 Оплатить за 1 BYN", "callback_data": "tripwire_1byn"},
            ],
            [
                {"text": "📦 Варианты аптечек", "callback_data": "view_kits"},
                {"text": "👤 Обо мне", "callback_data": "about_me"},
            ],
            [
                {"text": "⭐ Отзывы", "callback_data": "reviews"},
                {"text": "❓ FAQ", "callback_data": "faq"},
            ],
            [
                {"text": "🧠 Проверить знания!", "callback_data": "test_knowledge"},
            ]
        ]
    else:
        buttons = [
            [
                {"text": "📦 Варианты аптечек", "callback_data": "view_kits"},
                {"text": "👤 Обо мне", "callback_data": "about_me"},
            ],
            [
                {"text": "⭐ Отзывы", "callback_data": "reviews"},
                {"text": "❓ FAQ", "callback_data": "faq"},
            ],
            [
                {"text": "🧠 Пройти тест!", "callback_data": "take_test"},
            ]
        ]
    
    return create_inline_keyboard(buttons)


def kits_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню аптечек"""
    buttons = [
        [
            {"text": "👨‍👩‍👧‍👦 Семейная аптечка на год", "callback_data": "kit_family"},
            {"text": "🌸 Летняя-весенняя", "callback_data": "kit_summer"},
        ],
        [
            {"text": "👶 Детская", "callback_data": "kit_child"},
            {"text": "✈️ В отпуск", "callback_data": "kit_vacation"},
        ],
        [
            {"text": "⬅️ Назад", "callback_data": "back_to_main"},
        ]
    ]
    
    return create_inline_keyboard(buttons)


def about_me_keyboard() -> InlineKeyboardMarkup:
    """Меню 'Обо мне'"""
    buttons = [
        [
            {"text": "📖 Получить гайд за 1 руб.", "callback_data": "get_guide"},
        ],
        [
            {"text": "📦 Варианты аптечек", "callback_data": "view_kits"},
            {"text": "⭐ Отзывы", "callback_data": "reviews"},
        ],
        [
            {"text": "⬅️ Назад", "callback_data": "back_to_main"},
        ]
    ]
    
    return create_inline_keyboard(buttons)


def faq_keyboard() -> InlineKeyboardMarkup:
    """FAQ меню"""
    buttons = [
        [
            {"text": "🏥 Где купить лекарства?", "callback_data": "faq_where_buy"},
            {"text": "📅 Актуальность аптечек", "callback_data": "faq_relevance"},
        ],
        [
            {"text": "💰 Сколько стоят лекарства?", "callback_data": "faq_price"},
            {"text": "📋 Как выглядит аптечка?", "callback_data": "faq_looks"},
        ],
        [
            {"text": "❓ Свой вопрос", "callback_data": "faq_custom"},
        ],
        [
            {"text": "⬅️ Назад", "callback_data": "back_to_main"},
        ]
    ]
    
    return create_inline_keyboard(buttons)


def payment_keyboard(payment_url: str, product_name: str) -> InlineKeyboardMarkup:
    """Клавиатура для оплаты"""
    buttons = [
        [
            {"text": f"💳 Оплатить {product_name}", "url": payment_url},
        ],
        [
            {"text": "⬅️ Назад", "callback_data": "back_to_kits"},
        ]
    ]
    
    return create_inline_keyboard(buttons)


def faq_response_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после ответа FAQ"""
    buttons = [
        [
            {"text": "👍 Отлично!", "callback_data": "faq_great"},
            {"text": "❓ Другой вопрос", "callback_data": "faq_another"},
        ]
    ]
    
    return create_inline_keyboard(buttons)


def test_question_keyboard(options: list, question_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для вопроса теста"""
    buttons = []
    
    # Добавляем варианты ответов
    for i, option in enumerate(options):
        buttons.append([
            {"text": f"{chr(65 + i)}) {option}", "callback_data": f"test_answer_{question_id}_{i}"}
        ])
    
    return create_inline_keyboard(buttons)


def test_result_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после завершения теста"""
    buttons = [
        [
            {"text": "🏠 Главное меню", "callback_data": "back_to_main"},
            {"text": "🔄 Пройти снова", "callback_data": "take_test"},
        ]
    ]
    
    return create_inline_keyboard(buttons)


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в меню"""
    buttons = [
        [
            {"text": "🏠 Главное меню", "callback_data": "back_to_main"},
        ]
    ]
    
    return create_inline_keyboard(buttons)
