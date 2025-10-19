"""
Process test answer use case
"""

from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from src.domain.entities.test_result import TestResult
from src.domain.repositories.test_repository import TestRepository
from src.domain.use_cases.test.test_questions import TestQuestionsService


class ProcessTestAnswerUseCase:
    """Use case для обработки ответа на вопрос теста"""
    
    def __init__(self, test_repository: TestRepository):
        self.test_repository = test_repository
    
    async def execute(
        self, 
        test_data: Dict[str, Any], 
        answer_index: int
    ) -> Dict[str, Any]:
        """
        Обработать ответ на вопрос
        
        Args:
            test_data: Данные теста
            answer_index: Индекс выбранного ответа
        
        Returns:
            Результат обработки ответа
        """
        try:
            current_question_id = test_data["current_question_id"]
            answers = test_data["answers"]
            
            # Получаем текущий вопрос
            question = TestQuestionsService.get_question_by_id(current_question_id)
            
            # Проверяем правильность ответа
            is_correct = TestQuestionsService.validate_answer(current_question_id, answer_index)
            
            # Сохраняем ответ
            answers[current_question_id] = {
                "answer_index": answer_index,
                "is_correct": is_correct,
                "answered_at": datetime.utcnow()
            }
            
            # Определяем следующий вопрос
            questions = TestQuestionsService.get_test_questions()
            current_index = next(i for i, q in enumerate(questions) if q.id == current_question_id)
            
            if current_index < len(questions) - 1:
                # Есть еще вопросы
                next_question = questions[current_index + 1]
                test_data["current_question_id"] = next_question.id
                
                return {
                    "is_test_completed": False,
                    "next_question": next_question,
                    "question_number": current_index + 2,
                    "total_questions": len(questions),
                    "test_data": test_data,
                    "current_answer_correct": is_correct,
                    "explanation": question.explanation
                }
            else:
                # Тест завершен
                return await self._complete_test(test_data)
                
        except Exception as e:
            logger.error(f"Error processing test answer: {e}")
            raise
    
    async def _complete_test(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Завершить тест и сохранить результат"""
        try:
            answers = test_data["answers"]
            user_id = test_data["user_id"]
            attempts = test_data["attempts"]
            
            # Подсчитываем результаты
            total_questions = len(TestQuestionsService.get_test_questions())
            correct_answers = sum(1 for answer in answers.values() if answer["is_correct"])
            score = correct_answers
            passed = score == total_questions
            
            # Создаем результат теста
            test_result = TestResult(
                id=0,  # Будет установлен после сохранения
                user_id=user_id,
                score=score,
                total_questions=total_questions,
                attempts=attempts,
                passed=passed,
                answers_json=answers,
                completed_at=datetime.utcnow(),
            )
            
            # Сохраняем результат
            await self.test_repository.create_test_result(test_result)
            
            # Формируем сообщение результата
            result_message = self._get_result_message(test_result)
            
            logger.info(f"Test completed for user {user_id}: score {score}/{total_questions}")
            
            return {
                "is_test_completed": True,
                "test_result": test_result,
                "result_message": result_message,
                "score": score,
                "total_questions": total_questions,
                "percentage": (score / total_questions) * 100
            }
            
        except Exception as e:
            logger.error(f"Error completing test: {e}")
            raise
    
    def _get_result_message(self, test_result: TestResult) -> str:
        """Получить сообщение результата теста"""
        if test_result.is_excellent:
            if test_result.attempts == 1:
                return "🎉 Кто это? Просто Киборг! Помешанный на аптечках!"
            else:
                return "🎉 Мы поняли, что ты можешь запомнить три слова!"
        else:
            return "😔 Не все ответы правильны, так что аптечку лучше [купить]"
