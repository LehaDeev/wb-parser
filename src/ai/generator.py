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

    def generate_reply(self, review_text, product_name="", rating=5, user_name="", pros="", cons=""):
        """Генерирует ответ на отзыв"""
        return self.generator.generate_reply(review_text, product_name, rating, user_name, pros, cons)
