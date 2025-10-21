"""
Генератор ответов с использованием российских AI API
"""

import requests
import json
import time
from typing import Optional
from src.config.providers import AIProvider, PROVIDER_CONFIGS
from src.ai.templates import get_fallback_response, replace_name_placeholder
from src.config.settings import settings

class RussianAIGenerator:
    """Генератор ответов с российскими AI провайдерами"""

    def __init__(self):
        self.providers = self._initialize_providers()
        self.current_provider = None
        self.fallback_generator = None

        # Инициализируем провайдеры по порядку приоритета
        self._select_provider()

    def _initialize_providers(self) -> dict:
        """Инициализирует доступные провайдеры"""
        providers = {}

        # Yandex GPT
        if hasattr(settings, 'YANDEX_API_KEY') and settings.YANDEX_API_KEY:
            providers[AIProvider.YANDEX_GPT] = {
                'config': PROVIDER_CONFIGS[AIProvider.YANDEX_GPT],
                'api_key': settings.YANDEX_API_KEY,
                'folder_id': getattr(settings, 'YANDEX_FOLDER_ID', '')
            }

        # GigaChat
        if hasattr(settings, 'GIGACHAT_API_KEY') and settings.GIGACHAT_API_KEY:
            providers[AIProvider.GIGA_CHAT] = {
                'config': PROVIDER_CONFIGS[AIProvider.GIGA_CHAT],
                'api_key': settings.GIGACHAT_API_KEY
            }

        # Всегда доступен fallback
        providers[AIProvider.FALLBACK] = {
            'config': PROVIDER_CONFIGS[AIProvider.FALLBACK]
        }

        return providers

    def _select_provider(self):
        """Выбирает рабочий провайдер"""
        # Пробуем провайдеры по порядку приоритета
        for provider in [AIProvider.YANDEX_GPT, AIProvider.GIGA_CHAT]:
            if provider in self.providers:
                if self._test_provider(provider):
                    self.current_provider = provider
                    print(f"✅ Выбран провайдер: {self.providers[provider]['config']['name']}")
                    return

        # Если ни один API не работает, используем fallback
        self.current_provider = AIProvider.FALLBACK
        print("🔄 Используем локальные шаблоны (все API недоступны)")

    def _test_provider(self, provider: AIProvider) -> bool:
        """Тестирует подключение к провайдеру"""
        try:
            test_prompt = "Тестовое сообщение"
            response = self._make_request(provider, test_prompt)
            return response is not None and len(response) > 0
        except:
            return False

    def _make_request(self, provider: AIProvider, prompt: str) -> Optional[str]:
        """Выполняет запрос к выбранному провайдеру"""
        provider_config = self.providers[provider]
        config = provider_config['config']

        try:
            if provider == AIProvider.YANDEX_GPT:
                return self._call_yandex_gpt(provider_config, prompt)
            elif provider == AIProvider.GIGA_CHAT:
                return self._call_gigachat(provider_config, prompt)
            else:
                return None
        except Exception as e:
            print(f"❌ Ошибка {config['name']}: {e}")
            return None

    def _call_yandex_gpt(self, provider_config: dict, prompt: str) -> Optional[str]:
        """Вызывает Yandex GPT API"""
        url = provider_config['config']['base_url']

        headers = {
            "Authorization": f"Api-Key {provider_config['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "modelUri": f"gpt://{provider_config['folder_id']}/{provider_config['config']['model']}",
            "completionOptions": {
                "stream": False,
                "temperature": provider_config['config']['temperature'],
                "maxTokens": provider_config['config']['max_tokens']
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты представитель службы поддержки интернет-магазина. Отвечай вежливо и по делу."
                },
                {
                    "role": "user",
                    "text": prompt
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result['result']['alternatives'][0]['message']['text']

    def _call_gigachat(self, provider_config: dict, prompt: str) -> Optional[str]:
        """Вызывает GigaChat API"""
        url = provider_config['config']['base_url']

        # Для GigaChat нужно получить access token
        access_token = self._get_gigachat_token(provider_config['api_key'])
        if not access_token:
            return None

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "model": provider_config['config']['model'],
            "messages": [
                {
                    "role": "system",
                    "content": "Ты представитель службы поддержки интернет-магазина. Отвечай вежливо и по делу."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": provider_config['config']['max_tokens'],
            "temperature": provider_config['config']['temperature']
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']

    def _get_gigachat_token(self, api_key: str) -> Optional[str]:
        """Получает access token для GigaChat"""
        try:
            url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

            headers = {
                "Authorization": f"Basic {api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }

            data = {
                "scope": "GIGACHAT_API_PERS"
            }

            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result['access_token']
        except Exception as e:
            print(f"❌ Ошибка получения токена GigaChat: {e}")
            return None

    def generate_reply(self, review_text: str, product_name: str = "",
                      rating: int = 5, user_name: str = "",
                      pros: str = "", cons: str = "") -> str:
        """Генерирует ответ на отзыв"""

        # Создаем промпт
        prompt = self._build_prompt(review_text, product_name, rating, user_name, pros, cons)

        # Пробуем текущий провайдер
        if self.current_provider != AIProvider.FALLBACK:
            print(f"🤖 Генерация через {self.providers[self.current_provider]['config']['name']}...")
            response = self._make_request(self.current_provider, prompt)

            if response:
                final_response = replace_name_placeholder(response, user_name)
                print(f"✅ Ответ сгенерирован: {final_response[:80]}...")
                return final_response
            else:
                print("🔄 Провайдер не ответил, пробуем следующий...")
                self._try_next_provider()

        # Используем fallback
        return get_fallback_response(rating, user_name)

    def _try_next_provider(self):
        """Пробует следующий доступный провайдер"""
        current_index = list(self.providers.keys()).index(self.current_provider)
        next_providers = list(self.providers.keys())[current_index + 1:]

        for provider in next_providers:
            if provider != AIProvider.FALLBACK and self._test_provider(provider):
                self.current_provider = provider
                print(f"🔄 Переключились на: {self.providers[provider]['config']['name']}")
                return

        # Если ничего не работает, используем fallback
        self.current_provider = AIProvider.FALLBACK
        print("🔄 Используем локальные шаблоны")

    def _build_prompt(self, review_text: str, product_name: str, rating: int,
                     user_name: str, pros: str, cons: str) -> str:
        """Строит промпт для AI"""

        review_info = []
        if product_name:
            review_info.append(f"Товар: {product_name}")
        if pros:
            review_info.append(f"Плюсы: {pros}")
        if cons:
            review_info.append(f"Минусы: {cons}")

        review_context = "\n".join(review_info) if review_info else "Дополнительная информация не указана"

        name_context = f"Имя покупателя: {user_name}" if user_name else "Имя покупателя не указано"

        return f"""
        Отзыв покупателя: "{review_text}"

        Рейтинг: {rating}/5
        {review_context}
        {name_context}

        Составь вежливый ответ представителя службы поддержки (2-3 предложения):
        - Поблагодари за отзыв
        - Упоминай ключевую мысль отзыва
        - Будь дружелюбным и профессиональным
        - Не используй шаблонные фразы
        - Используй обращение по имени если оно указано

        Ответ:
        """
