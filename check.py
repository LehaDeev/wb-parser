#!/usr/bin/env python3
"""
Быстрая проверка состояния бота
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.config.settings import settings
from src.api.wb_client import WBAPIClient
from src.ai.generator import AIGenerator

def quick_check():
    """Быстрая проверка основных компонентов"""
    print("🔍 БЫСТРАЯ ПРОВЕРКА БОТА")
    print("=" * 40)

    # Проверка настроек
    print("⚙️  Настройки:")
    print(f"   WB API Key: {'✅' if settings.WB_API_KEY else '❌'}")
    print(f"   Supplier ID: {'✅' if settings.SUPPLIER_ID else '❌'}")
    print(f"   AI Provider: {settings.AI_PROVIDER}")
    print(f"   Test Mode: {settings.TEST_MODE}")

    # Проверка API
    print("\n🌐 API Wildberries:")
    try:
        client = WBAPIClient(test_mode=True)
        reviews = client.get_unanswered_reviews()
        print(f"   ✅ Клиент работает ({len(reviews)} тестовых отзывов)")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # Проверка AI
    print("\n🤖 AI Генератор:")
    try:
        ai = AIGenerator(test_mode=True)
        response = ai.generate_reply("Тестовый отзыв", "Тестовый товар", 5, "Тест")
        print(f"   ✅ Генератор работает: {response[:50]}...")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    print("\n💡 Для полной диагностики запустите: python scripts/status.py")

if __name__ == "__main__":
    quick_check()
