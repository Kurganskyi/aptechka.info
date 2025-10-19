"""
Test questions data
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class TestQuestion:
    """Вопрос теста"""
    id: int
    question: str
    options: List[str]
    correct_answer: int  # Индекс правильного ответа (0-3)
    explanation: str


class TestQuestionsService:
    """Сервис для работы с вопросами теста"""
    
    @staticmethod
    def get_test_questions() -> List[TestQuestion]:
        """Получить список вопросов теста"""
        return [
            TestQuestion(
                id=1,
                question="Какой препарат НЕ следует давать детям до 12 лет при высокой температуре?",
                options=[
                    "Парацетамол",
                    "Аспирин", 
                    "Ибупрофен",
                    "Нурофен"
                ],
                correct_answer=1,  # Аспирин
                explanation="Аспирин нельзя давать детям до 12 лет из-за риска развития синдрома Рея."
            ),
            TestQuestion(
                id=2,
                question="При какой температуре рекомендуется сбивать жар у взрослого?",
                options=[
                    "Выше 37.5°C",
                    "Выше 38.0°C",
                    "Выше 38.5°C", 
                    "Выше 39.0°C"
                ],
                correct_answer=2,  # Выше 38.5°C
                explanation="У взрослых температуру сбивают при 38.5°C и выше, если нет других показаний."
            ),
            TestQuestion(
                id=3,
                question="Как правильно хранить жидкие лекарства в холодильнике?",
                options=[
                    "В дверце холодильника",
                    "На нижней полке",
                    "В морозилке",
                    "На верхней полке"
                ],
                correct_answer=1,  # На нижней полке
                explanation="Жидкие лекарства лучше хранить на нижней полке холодильника для стабильной температуры."
            ),
            TestQuestion(
                id=4,
                question="Какой срок годности у открытого флакона с глазными каплями?",
                options=[
                    "1 месяц",
                    "3 месяца", 
                    "6 месяцев",
                    "До окончания срока годности"
                ],
                correct_answer=0,  # 1 месяц
                explanation="Открытый флакон с глазными каплями можно использовать не более 1 месяца."
            ),
            TestQuestion(
                id=5,
                question="При каких симптомах НЕ следует принимать обезболивающие?",
                options=[
                    "Головная боль",
                    "Острая боль в животе",
                    "Боль в спине",
                    "Зубная боль"
                ],
                correct_answer=1,  # Острая боль в животе
                explanation="При острой боли в животе нельзя принимать обезболивающие до осмотра врача."
            ),
            TestQuestion(
                id=6,
                question="Как правильно принимать таблетки?",
                options=[
                    "С любым количеством воды",
                    "С полным стаканом воды",
                    "Запивая кофе",
                    "Натощак всегда"
                ],
                correct_answer=1,  # С полным стаканом воды
                explanation="Таблетки следует запивать полным стаканом воды для лучшего усвоения."
            )
        ]
    
    @staticmethod
    def get_question_by_id(question_id: int) -> TestQuestion:
        """Получить вопрос по ID"""
        questions = TestQuestionsService.get_test_questions()
        for question in questions:
            if question.id == question_id:
                return question
        raise ValueError(f"Question with id {question_id} not found")
    
    @staticmethod
    def validate_answer(question_id: int, answer_index: int) -> bool:
        """Проверить правильность ответа"""
        question = TestQuestionsService.get_question_by_id(question_id)
        return answer_index == question.correct_answer
