"""
Start test use case
"""

from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

from src.domain.entities.test_result import TestResult
from src.domain.entities.user import User
from src.domain.repositories.test_repository import TestRepository
from src.domain.use_cases.test.test_questions import TestQuestionsService
from src.domain.exceptions import TestAlreadyCompletedException


class StartTestUseCase:
    """Use case для начала теста"""
    
    def __init__(self, test_repository: TestRepository):
        self.test_repository = test_repository
    
    async def execute(self, user: User) -> Dict[str, Any]:
        """
        Начать тест для пользователя
        
        Args:
            user: Пользователь
        
        Returns:
            Словарь с данными для начала теста
        """
        try:
            # Проверяем, есть ли уже результаты тестов
            existing_results = await self.test_repository.get_user_test_results(user.id)
            
            if existing_results:
                latest_result = existing_results[0]  # Самый последний результат
                attempts = latest_result.attempts + 1
            else:
                attempts = 1
            
            # Получаем первый вопрос
            questions = TestQuestionsService.get_test_questions()
            first_question = questions[0]
            
            # Подготавливаем данные для ответа
            test_data = {
                "user_id": user.id,
                "current_question_id": first_question.id,
                "attempts": attempts,
                "answers": {},  # Будет заполняться по мере прохождения
                "started_at": datetime.utcnow(),
            }
            
            logger.info(f"Test started for user {user.id}, attempt {attempts}")
            
            return {
                "question": first_question,
                "question_number": 1,
                "total_questions": len(questions),
                "attempts": attempts,
                "test_data": test_data
            }
            
        except Exception as e:
            logger.error(f"Error starting test for user {user.id}: {e}")
            raise
