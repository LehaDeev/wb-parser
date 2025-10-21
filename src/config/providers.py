"""
Конфигурация российских AI провайдеров
"""

from enum import Enum

class AIProvider(Enum):
    YANDEX_GPT = "yandex_gpt"
    GIGA_CHAT = "giga_chat"
    KANDINSKY = "kandinsky"
    FALLBACK = "fallback"

# Настройки провайдеров
PROVIDER_CONFIGS = {
    AIProvider.YANDEX_GPT: {
        "name": "Yandex GPT",
        "base_url": "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        "model": "yandexgpt-lite",
        "max_tokens": 150,
        "temperature": 0.7
    },
    AIProvider.GIGA_CHAT: {
        "name": "GigaChat",
        "base_url": "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        "model": "GigaChat",
        "max_tokens": 150,
        "temperature": 0.7
    },
    AIProvider.FALLBACK: {
        "name": "Локальные шаблоны",
        "model": "fallback",
        "max_tokens": 150,
        "temperature": 0.7
    }
}
