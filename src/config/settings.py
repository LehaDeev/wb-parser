import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Настройки приложения"""

    # API Keys - Wildberries
    WB_API_KEY: str = os.getenv('WB_API_KEY', '')
    SUPPLIER_ID: str = os.getenv('SUPPLIER_ID', '')

    # App Settings
    CHECK_INTERVAL: int = int(os.getenv('CHECK_INTERVAL', '30'))
    REQUEST_DELAY: float = 0.34
    TEST_MODE: bool = os.getenv('TEST_MODE', 'false').lower() == 'true'

    # API URLs
    WB_BASE_URL: str = "https://feedbacks-api.wildberries.ru/api/v1"

    # AI Settings
    AI_PROVIDER: str = os.getenv('AI_PROVIDER', 'free')  # free, russian, fallback

    # Российские AI провайдеры
    YANDEX_API_KEY: str = os.getenv('YANDEX_API_KEY', '')
    YANDEX_FOLDER_ID: str = os.getenv('YANDEX_FOLDER_ID', '')
    GIGACHAT_API_KEY: str = os.getenv('GIGACHAT_API_KEY', '')

    @property
    def has_russian_ai(self) -> bool:
        """Проверяет, настроены ли российские AI провайдеры"""
        return bool(self.YANDEX_API_KEY or self.GIGACHAT_API_KEY)

settings = Settings()
