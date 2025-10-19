"""
FSM States для бота
"""

from aiogram.fsm.state import State, StatesGroup


class TestStates(StatesGroup):
    """Состояния для системы тестирования"""
    waiting_for_answer = State()  # Ожидание ответа на вопрос
    test_completed = State()     # Тест завершен


class FAQStates(StatesGroup):
    """Состояния для FAQ"""
    waiting_for_question = State()  # Ожидание пользовательского вопроса
