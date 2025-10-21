#!/usr/bin/env python3
"""
Тестирование функциональности Wildberries Feedback Bot
"""

import sys
import os
import time
from datetime import datetime

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(__file__) + '/..')

try:
    from src.api.wb_client import WBAPIClient
    from src.ai.generator import AIGenerator
    from src.core.manager import ResponseManager
    from src.core.processor import ReviewProcessor
    from src.config.settings import settings
    print("✅ Модули успешно загружены")
except ImportError as e:
    print(f"❌ Ошибка импорта модулей: {e}")
    sys.exit(1)

def print_test_section(title, emoji="🧪"):
    """Печатает заголовок тестовой секции"""
    print(f"\n{emoji} {title}")
    print("─" * 60)

def test_api_connection():
    """Тестирует подключение к API Wildberries"""
    print_test_section("ТЕСТ ПОДКЛЮЧЕНИЯ К API", "🌐")

    client = WBAPIClient(test_mode=False)

    tests = [
        ("Базовая проверка подключения", lambda: client.has_unseen_feedbacks()),
        ("Получение статистики", lambda: client.get_unanswered_count()),
        ("Получение списка отзывов", lambda: client.get_unanswered_reviews()),
    ]

    all_passed = True

    for test_name, test_func in tests:
        try:
            print(f"🔍 {test_name}...")
            result = test_func()
            print(f"   ✅ Успешно: {type(result).__name__}")
            all_passed = all_passed and True
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            all_passed = False

    return all_passed

def test_ai_generator():
    """Тестирует генератор ответов ИИ"""
    print_test_section("ТЕСТ ИИ ГЕНЕРАТОРА", "🤖")

    ai = AIGenerator(test_mode=False)

    test_cases = [
        {
            "name": "Позитивный отзыв с именем",
            "review": "Отличный товар! Качество на высоте, доставка быстрая.",
            "rating": 5,
            "user_name": "Анна",
            "product": "Футболка хлопковая"
        },
        {
            "name": "Негативный отзыв",
            "review": "Товар пришел с дефектом, очень расстроен качеством.",
            "rating": 2,
            "user_name": "Иван",
            "product": "Наушники беспроводные"
        },
        {
            "name": "Нейтральный отзыв без имени",
            "review": "Нормальный товар за свои деньги, но есть недочеты.",
            "rating": 3,
            "user_name": "",
            "product": "Чехол для телефона"
        },
        {
            "name": "Очень негативный отзыв",
            "review": "Ужасное качество! Товар сломался через день использования.",
            "rating": 1,
            "user_name": "Мария",
            "product": "Беспроводная зарядка"
        },
        {
            "name": "Очень позитивный отзыв",
            "review": "Просто восторг! Лучшая покупка за последнее время!",
            "rating": 5,
            "user_name": "Дмитрий",
            "product": "Умные часы"
        }
    ]

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Тест {i}: {test_case['name']}")
        print(f"   💬 Отзыв: {test_case['review']}")
        print(f"   ⭐ Рейтинг: {test_case['rating']}/5")
        print(f"   👤 Имя: '{test_case['user_name']}'")
        print(f"   🏷️  Товар: {test_case['product']}")

        try:
            start_time = time.time()
            response = ai.generate_reply(
                review_text=test_case['review'],
                product_name=test_case['product'],
                rating=test_case['rating'],
                user_name=test_case['user_name']
            )
            response_time = time.time() - start_time

            print(f"   ✅ Ответ ({response_time:.2f} сек): {response}")

            # Проверка качества ответа
            if not response or len(response.strip()) < 10:
                print("   ⚠️  Слишком короткий ответ")
                all_passed = False
            elif "[ОШИБКА]" in response:
                print("   ❌ Ответ содержит ошибку")
                all_passed = False
            else:
                print("   ✅ Ответ корректный")

        except Exception as e:
            print(f"   ❌ Ошибка генерации: {e}")
            all_passed = False

    return all_passed

def test_review_processor():
    """Тестирует обработчик отзывов"""
    print_test_section("ТЕСТ ОБРАБОТЧИКА ОТЗЫВОВ", "⚙️")

    ai = AIGenerator(test_mode=True)  # Тестовый режим для предсказуемости
    processor = ReviewProcessor(ai)

    # Создаем тестовые отзывы
    test_reviews = []
    for i in range(3):
        test_reviews.append(type('MockReview', (), {
            'id': f'test_review_{i}',
            'text': f'Тестовый отзыв {i} с содержательным текстом',
            'product_name': f'Тестовый товар {i}',
            'rating': 4 if i % 2 == 0 else 3,
            'user_name': f'Тестовый пользователь {i}',
            'pros': 'Хорошее качество' if i % 2 == 0 else '',
            'cons': '' if i % 2 == 0 else 'Небольшие недочеты',
            'has_text': True
        })())

    print(f"📥 Создано {len(test_reviews)} тестовых отзывов")

    try:
        # Тестируем обработку
        results = processor.process_reviews(test_reviews)

        print(f"📊 Обработано отзывов: {len(results)}")

        for i, result in enumerate(results, 1):
            status = "✅" if result["success"] else "❌"
            print(f"   {status} Отзыв {i}: {result['review'].id} -> {len(result['reply'])} символов")

        # Проверяем, что отзывы помечены как обработанные
        for review in test_reviews:
            if review.id in processor.processed_ids:
                print(f"   ✅ Отзыв {review.id} помечен как обработанный")
            else:
                print(f"   ❌ Отзыв {review.id} не помечен как обработанный")
                return False

        return len(results) == len(test_reviews)

    except Exception as e:
        print(f"   ❌ Ошибка обработки: {e}")
        return False

def test_response_manager():
    """Тестирует менеджер ответов"""
    print_test_section("ТЕСТ МЕНЕДЖЕРА ОТВЕТОВ", "👨‍💼")

    # Тест в тестовом режиме
    print("🔧 Тестовый режим...")
    test_manager = ResponseManager(test_mode=True)

    try:
        # Запускаем обработку
        start_time = time.time()
        test_manager.process_new_reviews()
        execution_time = time.time() - start_time

        print(f"   ✅ Обработка завершена за {execution_time:.2f} сек")
        print("   ✅ Логика менеджера работает корректно")

        # Тест в реальном режиме (только инициализация)
        print("\n🔧 Реальный режим (инициализация)...")
        real_manager = ResponseManager(test_mode=False)
        print("   ✅ Менеджер инициализирован")
        print("   ✅ Компоненты загружены")

        return True

    except Exception as e:
        print(f"   ❌ Ошибка менеджера: {e}")
        return False

def test_rate_limiting():
    """Тестирует ограничитель запросов"""
    print_test_section("ТЕСТ ОГРАНИЧИТЕЛЯ ЗАПРОСОВ", "⏱️")

    from src.api.rate_limiter import RateLimiter

    try:
        limiter = RateLimiter(delay=0.1)  # Маленькая задержка для теста

        print("⏰ Тестирование задержки между запросами...")

        start_time = time.time()

        # Выполняем несколько запросов подряд
        for i in range(3):
            limiter.wait_if_needed()
            print(f"   📨 Запрос {i+1} выполнен")

        total_time = time.time() - start_time

        # Должно быть минимум 0.2 сек (2 задержки по 0.1 сек)
        if total_time >= 0.2:
            print(f"   ✅ Ограничитель работает: {total_time:.2f} сек")
            return True
        else:
            print(f"   ❌ Ограничитель не работает: {total_time:.2f} сек")
            return False

    except Exception as e:
        print(f"   ❌ Ошибка ограничителя: {e}")
        return False

def test_error_handling():
    """Тестирует обработку ошибок"""
    print_test_section("ТЕСТ ОБРАБОТКИ ОШИБОК", "🚨")

    ai = AIGenerator(test_mode=False)

    # Тестовые случаи с потенциальными ошибками
    error_cases = [
        {
            "name": "Пустой отзыв",
            "review": "",
            "rating": 5,
            "user_name": "Тест"
        },
        {
            "name": "Очень короткий отзыв",
            "review": "ok",
            "rating": 5,
            "user_name": "Тест"
        },
        {
            "name": "Отзыв только с цифрами",
            "review": "5 5 5",
            "rating": 5,
            "user_name": "Тест"
        },
        {
            "name": "Отзыв с специальными символами",
            "review": "!!! @@@ ### $$$",
            "rating": 3,
            "user_name": "Тест"
        }
    ]

    all_handled = True

    for case in error_cases:
        print(f"🔍 {case['name']}...")

        try:
            response = ai.generate_reply(
                review_text=case['review'],
                product_name="Тестовый товар",
                rating=case['rating'],
                user_name=case['user_name']
            )

            if response and len(response.strip()) > 0:
                print(f"   ✅ Обработано: {response[:50]}...")
            else:
                print("   ⚠️  Пустой ответ, но без ошибки")

        except Exception as e:
            print(f"   ❌ Необработанная ошибка: {e}")
            all_handled = False

    return all_handled

def performance_test():
    """Тест производительности"""
    print_test_section("ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ", "⚡")

    ai = AIGenerator(test_mode=True)  # Тестовый режим для скорости

    print("🏃 Тест скорости генерации 5 ответов...")

    start_time = time.time()

    for i in range(5):
        response = ai.generate_reply(
            review_text=f"Тестовый отзыв для проверки производительности {i}",
            product_name="Тестовый товар",
            rating=4,
            user_name="Тест"
        )
        print(f"   📝 Ответ {i+1}: {len(response)} символов")

    total_time = time.time() - start_time
    avg_time = total_time / 5

    print(f"📊 Результаты:")
    print(f"   🕒 Общее время: {total_time:.2f} сек")
    print(f"   ⚡ Среднее время: {avg_time:.2f} сек/ответ")

    if avg_time < 2.0:  # Реалистичный порог для тестового режима
        print("   ✅ Производительность в норме")
        return True
    else:
        print("   ⚠️  Производительность низкая")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 WILDBERRIES FEEDBACK BOT - ТЕСТИРОВАНИЕ")
    print("=" * 70)
    print(f"🕒 Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Список тестов
    tests = [
        ("Подключение к API", test_api_connection),
        ("Ограничитель запросов", test_rate_limiting),
        ("ИИ генератор", test_ai_generator),
        ("Обработчик отзывов", test_review_processor),
        ("Менеджер ответов", test_response_manager),
        ("Обработка ошибок", test_error_handling),
        ("Производительность", performance_test),
    ]

    results = []

    # Запуск тестов
    for test_name, test_func in tests:
        try:
            print(f"\n🎯 Запуск теста: {test_name}")
            result = test_func()
            results.append((test_name, result))
            status = "✅ ПРОЙДЕН" if result else "❌ НЕ ПРОЙДЕН"
            print(f"📋 Результат: {status}")
        except Exception as e:
            print(f"💥 Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))

    # Итоговый отчет
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
    print("=" * 70)

    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)

    print(f"✅ Пройдено тестов: {passed_tests}/{total_tests}")
    print(f"📈 Успешность: {(passed_tests/total_tests)*100:.1f}%")

    print("\n📋 Детализация:")
    for test_name, result in results:
        status_emoji = "✅" if result else "❌"
        print(f"   {status_emoji} {test_name}")

    # Рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ:")
    if passed_tests == total_tests:
        print("   🎉 Все системы работают отлично!")
        print("   🚀 Бот готов к работе в продакшене")
    elif passed_tests >= total_tests * 0.7:
        print("   ⚠️  Большинство тестов пройдено")
        print("   🔧 Проверьте проблемные компоненты")
    else:
        print("   ❌ Много неудачных тестов")
        print("   🛠️  Требуется серьезная отладка")

    print(f"\n🕒 Время окончания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Возвращаем код выхода
    return 0 if passed_tests == total_tests else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
