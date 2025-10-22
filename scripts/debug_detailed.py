#!/usr/bin/env python3
"""
Расширенная диагностика API Wildberries
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__) + '/..')

from src.api.wb_client import WBAPIClient
from src.config.settings import settings

def debug_detailed():
    print("🔍 РАСШИРЕННАЯ ДИАГНОСТИКА API WILDBERRIES")
    print("=" * 60)

    client = WBAPIClient(test_mode=False)

    # Тестируем разные параметры запроса
    test_params = [
        {"isAnswered": False, "take": 50, "skip": 0},
        {"isAnswered": False, "take": 100, "skip": 0},
        {"take": 50, "skip": 0},  # Без фильтра isAnswered
        {"isAnswered": False, "take": 50, "skip": 0, "order": "dateAsc"},
    ]

    for i, params in enumerate(test_params, 1):
        print(f"\n🧪 Тест {i}: Параметры {params}")

        result = client._make_request("GET", "feedbacks", params=params)

        if result.get("error"):
            print(f"   ❌ Ошибка: {result.get('errorText')}")
            continue

        data = result.get("data", {})
        feedbacks = data.get("feedbacks", [])

        print(f"   📥 Получено отзывов: {len(feedbacks)}")

        # Анализируем каждый отзыв
        for j, feedback in enumerate(feedbacks):
            feedback_id = feedback.get('id', 'N/A')
            has_text = bool(feedback.get('text', '').strip())
            is_answered = feedback.get('answered', True)
            rating = feedback.get('productValuation', 'N/A')
            was_viewed = feedback.get('wasViewed', False)

            status = "✅" if has_text and not is_answered else "⚠️"

            print(f"      {status} Отзыв {j+1}: ID={feedback_id}")
            print(f"         Текст: {'✅' if has_text else '❌'}")
            print(f"         Отвечен: {'✅' if is_answered else '❌'}")
            print(f"         Просмотрен: {'✅' if was_viewed else '❌'}")
            print(f"         Рейтинг: {rating}")

            if has_text:
                text_preview = feedback.get('text', '')[:80] + "..." if len(feedback.get('text', '')) > 80 else feedback.get('text', '')
                print(f"         Текст: {text_preview}")

            print(f"         Полные данные: {json.dumps(feedback, ensure_ascii=False, indent=8)}")

if __name__ == "__main__":
    debug_detailed()
