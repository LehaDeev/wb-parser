"""
Основной генератор ответов
"""

from .free_generator import FreeAIGenerator
from .fallback_generator import FallbackAIGenerator
from .russian_generator import RussianAIGenerator
from src.config.settings import settings

class AIGenerator:
    """Универсальный генератор ответов"""

    def __init__(self, test_mode=False):
        self.test_mode = test_mode

        if test_mode:
            self.generator = FallbackAIGenerator()
            print("🔧 ТЕСТОВЫЙ РЕЖИМ: Используем локальные шаблоны")
        else:
            if settings.AI_PROVIDER == "russian" and settings.has_russian_ai:
                self.generator = RussianAIGenerator()
                print("🇷🇺 Используем российские AI провайдеры")
            elif settings.AI_PROVIDER == "free":
                self.generator = FreeAIGenerator()
                print("🆓 Используем бесплатный AI генератор")
            else:
                self.generator = FallbackAIGenerator()
                print("🔄 Используем локальные шаблоны")

    def generate_reply(self, review_text: str, product_name: str = "",
                    rating: int = 5, user_name: str = "",
                    pros: str = "", cons: str = "") -> str:
        """Генерирует ответ на отзыв с учетом всех полей"""

        # Если review_text уже содержит объединенные данные, используем как есть
        # Иначе создаем полный текст из отдельных полей
        if "Отзыв:" not in review_text and "Преимущества:" not in review_text:
            full_review = []
            if review_text.strip():
                full_review.append(f"Отзыв: {review_text}")
            if pros.strip():
                full_review.append(f"Преимущества: {pros}")
            if cons.strip():
                full_review.append(f"Недостатки: {cons}")

            if full_review:
                review_text = "\n".join(full_review)

        return self.generator.generate_reply(review_text, product_name, rating, user_name, pros, cons)
