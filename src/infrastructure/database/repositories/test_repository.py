"""
Test repository implementation
"""

from typing import Optional, List
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.domain.entities.test_result import TestResult
from src.domain.repositories.test_repository import TestRepository
from src.infrastructure.database.models.test import TestResultModel


class SQLAlchemyTestRepository(TestRepository):
    """Реализация репозитория тестов через SQLAlchemy"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_test_result(self, test_result: TestResult) -> TestResult:
        """Создать результат теста"""
        try:
            test_result_model = TestResultModel(
                user_id=test_result.user_id,
                score=test_result.score,
                total_questions=test_result.total_questions,
                attempts=test_result.attempts,
                passed=test_result.passed,
                answers_json=test_result.answers_json,
                completed_at=test_result.completed_at,
                created_at=test_result.created_at,
            )
            
            self.session.add(test_result_model)
            await self.session.flush()
            
            # Обновляем ID в entity
            test_result.id = test_result_model.id
            
            logger.info(f"Test result created: {test_result.id} for user {test_result.user_id}")
            return test_result
            
        except Exception as e:
            logger.error(f"Error creating test result for user {test_result.user_id}: {e}")
            raise
    
    async def get_user_test_results(self, user_id: int) -> List[TestResult]:
        """Получить результаты тестов пользователя"""
        try:
            result = await self.session.execute(
                select(TestResultModel)
                .where(TestResultModel.user_id == user_id)
                .order_by(TestResultModel.completed_at.desc())
            )
            test_result_models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in test_result_models]
            
        except Exception as e:
            logger.error(f"Error getting user test results for {user_id}: {e}")
            raise
    
    async def get_latest_test_result(self, user_id: int) -> Optional[TestResult]:
        """Получить последний результат теста пользователя"""
        try:
            result = await self.session.execute(
                select(TestResultModel)
                .where(TestResultModel.user_id == user_id)
                .order_by(TestResultModel.completed_at.desc())
                .limit(1)
            )
            test_result_model = result.scalar_one_or_none()
            
            if test_result_model:
                return self._model_to_entity(test_result_model)
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest test result for user {user_id}: {e}")
            raise
    
    async def get_test_result_by_id(self, test_result_id: int) -> Optional[TestResult]:
        """Получить результат теста по ID"""
        try:
            result = await self.session.execute(
                select(TestResultModel).where(TestResultModel.id == test_result_id)
            )
            test_result_model = result.scalar_one_or_none()
            
            if test_result_model:
                return self._model_to_entity(test_result_model)
            return None
            
        except Exception as e:
            logger.error(f"Error getting test result by id {test_result_id}: {e}")
            raise
    
    async def update_test_result(self, test_result: TestResult) -> TestResult:
        """Обновить результат теста"""
        try:
            await self.session.execute(
                update(TestResultModel)
                .where(TestResultModel.id == test_result.id)
                .values(
                    score=test_result.score,
                    total_questions=test_result.total_questions,
                    attempts=test_result.attempts,
                    passed=test_result.passed,
                    answers_json=test_result.answers_json,
                    completed_at=test_result.completed_at,
                )
            )
            
            logger.info(f"Test result updated: {test_result.id}")
            return test_result
            
        except Exception as e:
            logger.error(f"Error updating test result {test_result.id}: {e}")
            raise
    
    async def get_test_statistics(self) -> dict:
        """Получить статистику тестов"""
        try:
            # Общее количество тестов
            total_tests_result = await self.session.execute(
                select(func.count(TestResultModel.id))
            )
            total_tests = total_tests_result.scalar() or 0
            
            # Количество пройденных тестов
            passed_tests_result = await self.session.execute(
                select(func.count(TestResultModel.id))
                .where(TestResultModel.passed == True)
            )
            passed_tests = passed_tests_result.scalar() or 0
            
            # Средний балл
            avg_score_result = await self.session.execute(
                select(func.avg(TestResultModel.score))
            )
            avg_score = avg_score_result.scalar() or 0
            
            # Количество уникальных пользователей
            unique_users_result = await self.session.execute(
                select(func.count(func.distinct(TestResultModel.user_id)))
            )
            unique_users = unique_users_result.scalar() or 0
            
            # Распределение по баллам
            score_distribution_result = await self.session.execute(
                select(
                    TestResultModel.score,
                    func.count(TestResultModel.id).label('count')
                )
                .group_by(TestResultModel.score)
                .order_by(TestResultModel.score)
            )
            score_distribution = {
                row.score: row.count 
                for row in score_distribution_result
            }
            
            return {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "avg_score": round(float(avg_score), 2) if avg_score else 0,
                "unique_users": unique_users,
                "score_distribution": score_distribution,
            }
            
        except Exception as e:
            logger.error(f"Error getting test statistics: {e}")
            raise
    
    def _model_to_entity(self, model: TestResultModel) -> TestResult:
        """Преобразование модели в entity"""
        return TestResult(
            id=model.id,
            user_id=model.user_id,
            score=model.score,
            total_questions=model.total_questions,
            attempts=model.attempts,
            passed=model.passed,
            answers_json=model.answers_json,
            completed_at=model.completed_at,
            created_at=model.created_at,
        )
