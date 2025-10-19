"""
Test handlers
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.domain.entities.user import User
from src.domain.repositories.test_repository import TestRepository
from src.domain.use_cases.test.start_test import StartTestUseCase
from src.domain.use_cases.test.process_test_answer import ProcessTestAnswerUseCase
from src.infrastructure.database.session import get_db_session
from src.infrastructure.database.repositories.test_repository import SQLAlchemyTestRepository
from src.presentation.keyboards.inline import (
    test_question_keyboard,
    back_to_menu_keyboard,
    test_result_keyboard
)
from src.presentation.states import TestStates

router = Router()


@router.callback_query(F.data == "take_test")
async def start_test(callback: CallbackQuery, state: FSMContext, user: User):
    """Начать тест"""
    try:
        await callback.answer()
        
        async with get_db_session() as session:
            test_repository = SQLAlchemyTestRepository(session)
            start_test_uc = StartTestUseCase(test_repository)
            
            test_data = await start_test_uc.execute(user)
            
            # Сохраняем данные теста в FSM
            await state.update_data(**test_data["test_data"])
            await state.set_state(TestStates.waiting_for_answer)
            
            # Отправляем первый вопрос
            question = test_data["question"]
            question_number = test_data["question_number"]
            total_questions = test_data["total_questions"]
            attempts = test_data["attempts"]
            
            await callback.message.edit_text(
                f"🧠 Тест из {total_questions} каверзных вопросов\n"
                f"Попытка: {attempts}\n"
                f"Вопрос {question_number} из {total_questions}\n\n"
                f"❓ {question.question}",
                reply_markup=test_question_keyboard(question.options, question.id)
            )
            
            logger.info(f"Test started for user {user.telegram_id}, question {question_number}")
        
    except Exception as e:
        logger.error(f"Error starting test: {e}")
        await callback.answer("Произошла ошибка при запуске теста", show_alert=True)


@router.callback_query(F.data.startswith("test_answer_"))
async def process_test_answer(callback: CallbackQuery, state: FSMContext, user: User):
    """Обработать ответ на вопрос теста"""
    try:
        await callback.answer()
        
        # Извлекаем данные из callback_data
        # Формат: test_answer_questionId_answerIndex
        parts = callback.data.split("_")
        question_id = int(parts[2])
        answer_index = int(parts[3])
        
        async with get_db_session() as session:
            test_repository = SQLAlchemyTestRepository(session)
            process_answer_uc = ProcessTestAnswerUseCase(test_repository)
            
            # Получаем данные теста
            test_data = await state.get_data()
            
            # Обрабатываем ответ
            result = await process_answer_uc.execute(test_data, answer_index)
            
            if result["is_test_completed"]:
                # Тест завершен
                await state.set_state(TestStates.test_completed)
                await state.clear()
                
                test_result = result["test_result"]
                score = result["score"]
                total_questions = result["total_questions"]
                percentage = result["percentage"]
                result_message = result["result_message"]
                
                await callback.message.edit_text(
                    f"🎯 Тест завершен!\n\n"
                    f"📊 Результат: {score} из {total_questions} ({percentage:.1f}%)\n\n"
                    f"{result_message}\n\n"
                    f"{'🎉 Поздравляем! Вы прошли тест!' if test_result.passed else '💡 Рекомендуем изучить наши аптечки для улучшения знаний!'}"
                )
                
                # Добавляем кнопку "Заявка в шоу 'Кто хочет стать Миллионером'" если тест пройден
                if test_result.passed:
                    await callback.message.answer(
                        "🎪 Заявка в шоу 'Кто хочет стать Миллионером'",
                        reply_markup=back_to_menu_keyboard()
                    )
                else:
                    await callback.message.answer(
                        "💊 Рекомендуем изучить наши аптечки!",
                        reply_markup=back_to_menu_keyboard()
                    )
                
                logger.info(f"Test completed for user {user.telegram_id}: {score}/{total_questions}")
                
            else:
                # Переходим к следующему вопросу
                await state.update_data(**result["test_data"])
                
                next_question = result["next_question"]
                question_number = result["question_number"]
                total_questions = result["total_questions"]
                is_correct = result["current_answer_correct"]
                explanation = result["explanation"]
                
                # Отправляем результат текущего вопроса
                await callback.message.edit_text(
                    f"{'✅ Правильно!' if is_correct else '❌ Неправильно'}\n\n"
                    f"💡 {explanation}\n\n"
                    f"Переходим к следующему вопросу..."
                )
                
                # Ждем немного и отправляем следующий вопрос
                await callback.message.answer(
                    f"🧠 Вопрос {question_number} из {total_questions}\n\n"
                    f"❓ {next_question.question}",
                    reply_markup=test_question_keyboard(next_question.options, next_question.id)
                )
                
                logger.info(f"Question {question_number} answered for user {user.telegram_id}")
        
    except Exception as e:
        logger.error(f"Error processing test answer: {e}")
        await callback.answer("Произошла ошибка при обработке ответа", show_alert=True)


@router.callback_query(F.data == "test_knowledge")
async def test_knowledge_info(callback: CallbackQuery):
    """Информация о тесте знаний"""
    try:
        await callback.answer()
        
        await callback.message.edit_text(
            "🧠 Проверить знания!\n\n"
            "Пройдите тест из 6 каверзных вопросов и проверьте свои знания об аптечках!\n\n"
            "Тест включает вопросы о:\n"
            "• Лекарствах для детей\n"
            "• Хранении медикаментов\n"
            "• Правильном приеме препаратов\n"
            "• Безопасности лекарств\n\n"
            "Готовы проверить свои знания?",
            reply_markup=back_to_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in test_knowledge_info: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)
