#!/usr/bin/env python3
"""
Проверка статуса бота и API Wildberries
"""

import sys
import os
from datetime import datetime

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(__file__) + '/..')

try:
    from src.api.wb_client import WBAPIClient
    from src.ai.generator import AIGenerator
    from src.config.settings import settings
    print("✅ Модули успешно загружены")
except ImportError as e:
    print(f"❌ Ошибка импорта модулей: {e}")
    sys.exit(1)

def print_section(title):
    """Печатает заголовок секции"""
    print(f"\n{title}")
    print("─" * 50)

def check_settings():
    """Проверяет настройки приложения"""
    print_section("⚙️  НАСТРОЙКИ ПРИЛОЖЕНИЯ")

    try:
        wb_status = "✅ Настроен" if settings.WB_API_KEY and len(settings.WB_API_KEY) > 10 else "❌ Не настроен"
        supplier_status = "✅ " + settings.SUPPLIER_ID if settings.SUPPLIER_ID else "⚠️  Не настроен"

        # Проверяем AI провайдер
        ai_provider = getattr(settings, 'AI_PROVIDER', 'fallback')
        if ai_provider == 'free':
            ai_status = "🆓 Бесплатные шаблоны"
        elif ai_provider == 'russian':
            # Проверяем российские провайдеры
            yandex_configured = hasattr(settings, 'YANDEX_API_KEY') and settings.YANDEX_API_KEY
            gigachat_configured = hasattr(settings, 'GIGACHAT_API_KEY') and settings.GIGACHAT_API_KEY

            if yandex_configured or gigachat_configured:
                providers = []
                if yandex_configured:
                    providers.append("Yandex GPT")
                if gigachat_configured:
                    providers.append("GigaChat")
                ai_status = f"🇷🇺 Российские AI: {', '.join(providers)}"
            else:
                ai_status = "🔄 Локальные шаблоны"
        else:
            ai_status = "🔄 Локальные шаблоны"

        print(f"🔐 WB API Key: {wb_status}")
        print(f"🏷️  Supplier ID: {supplier_status}")
        print(f"🤖 AI Провайдер: {ai_status}")
        print(f"⏰ Интервал проверки: {settings.CHECK_INTERVAL} минут")
        print(f"🔧 Тестовый режим: {'✅ ВКЛ' if settings.TEST_MODE else '✅ ВЫКЛ'}")

        # Все настройки в порядке если есть WB API ключ
        return bool(settings.WB_API_KEY and len(settings.WB_API_KEY) > 10)

    except Exception as e:
        print(f"❌ Ошибка при проверке настроек: {e}")
        return False
def check_wb_api():
    """Проверяет подключение к API Wildberries"""
    print_section("🌐 API WILDBERRIES")

    client = WBAPIClient(test_mode=False)

    try:
        # Проверка базового подключения
        print("🔍 Проверка подключения к API...")
        has_unseen = client.has_unseen_feedbacks()
        print("   ✅ API доступен")

        # Получение статистики
        print("📊 Получение статистики...")
        stats = client.get_unanswered_count()

        unanswered_total = stats.get('countUnanswered', 0)
        unanswered_today = stats.get('countUnansweredToday', 0)
        avg_rating = stats.get('valuation', 'N/A')

        print(f"   📈 Всего неотвеченных отзывов: {unanswered_total}")
        print(f"   📅 Новых отзывов сегодня: {unanswered_today}")
        print(f"   ⭐ Средняя оценка: {avg_rating}")

        # Проверка непросмотренных
        print("👀 Проверка непросмотренных...")
        result = client._make_request("GET", "new-feedbacks-questions")
        if not result.get("error"):
            data = result.get("data", {})
            has_feedbacks = data.get("hasNewFeedbacks", False)
            has_questions = data.get("hasNewQuestions", False)
            print(f"   📝 Непросмотренные отзывы: {'✅ ЕСТЬ' if has_feedbacks else '❌ НЕТ'}")
            print(f"   ❓ Непросмотренные вопросы: {'✅ ЕСТЬ' if has_questions else '❌ НЕТ'}")

        # Получение списка отзывов
        print("📋 Получение списка отзывов...")
        reviews = client.get_unanswered_reviews()
        print(f"   📄 Доступно для обработки: {len(reviews)} отзывов")

        # Показ последних отзывов
        if reviews:
            print(f"\n   🆕 Последние {min(3, len(reviews))} отзыва:")
            for i, review in enumerate(reviews[:3], 1):
                rating_emojis = "⭐" * review.rating
                print(f"      {i}. {rating_emojis} ({review.rating}/5)")
                print(f"         👤 {review.user_name if review.user_name else 'Аноним'}")
                print(f"         💬 {review.text[:80]}{'...' if len(review.text) > 80 else ''}")
                if review.pros or review.cons:
                    if review.pros:
                        print(f"         👍 {review.pros}")
                    if review.cons:
                        print(f"         👎 {review.cons}")

        return True

    except Exception as e:
        print(f"   ❌ Ошибка подключения к API: {e}")
        return False

def check_ai():
    """Проверяет работу ИИ генератора"""
    print_section("🤖 ИИ ГЕНЕРАТОР")

    try:
        from src.ai.generator import AIGenerator

        # Тест в тестовом режиме
        print("🧪 Тест в тестовом режиме...")
        test_ai = AIGenerator(test_mode=True)
        test_response = test_ai.generate_reply(
            review_text="Отличный товар!",
            product_name="Тестовый товар",
            rating=5,
            user_name="Анна"
        )
        print(f"   ✅ Тестовый режим: {test_response}")

        # Тест в реальном режиме
        print("🚀 Тест в реальном режиме...")
        real_ai = AIGenerator(test_mode=False)
        real_response = real_ai.generate_reply(
            review_text="Очень доволен покупкой!",
            product_name="Тестовый товар",
            rating=5,
            user_name="Иван"
        )
        print(f"   ✅ Реальный режим: {real_response}")

        # Проверяем качество ответа
        if real_response and len(real_response.strip()) > 10:
            print("   ✅ Генератор работает корректно")
            return True
        else:
            print("   ⚠️  Ответ слишком короткий")
            return False

    except Exception as e:
        print(f"   ❌ Ошибка ИИ генератора: {e}")
        return False

def check_system():
    """Проверяет системные параметры"""
    print_section("💻 СИСТЕМА")

    # Время работы
    print(f"🕒 Текущее время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Версия Python
    print(f"🐍 Версия Python: {sys.version.split()[0]}")

    # Доступность модулей
    modules = ['requests', 'openai', 'schedule', 'dotenv']
    available_modules = []
    for module in modules:
        try:
            __import__(module)
            available_modules.append(f"✅ {module}")
        except ImportError:
            available_modules.append(f"❌ {module}")

    print("📦 Зависимости: " + ", ".join(available_modules))

    # Проверяем что dotenv реально работает
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("🔧 python-dotenv: ✅ работает")
        return True
    except Exception as e:
        print(f"🔧 python-dotenv: ❌ ошибка - {e}")
        return False

def check_bot_status():
    """Проверяет статус бота"""
    print_section("🤖 СТАТУС БОТА")

    try:
        from src.core.manager import ResponseManager

        # Тест в тестовом режиме
        print("🧪 Тест обработки (тестовый режим)...")
        test_manager = ResponseManager(test_mode=True)
        test_manager.process_new_reviews()
        print("   ✅ Логика обработки работает")

        # Проверка реального режима
        print("🔧 Проверка реального режима...")
        real_manager = ResponseManager(test_mode=False)
        print("   ✅ Менеджер инициализирован")

        print("\n🎯 Бот готов к работе!")
        print("   📍 Запустите: python main.py")
        print("   🔍 Для проверки: python check.py")
        print("   ⏸️  Для остановки: Ctrl+C")

        return True

    except Exception as e:
        print(f"   ❌ Ошибка бота: {e}")
        return False

def main():
    """Основная функция проверки статуса"""
    print("🔍 WILDBERRIES FEEDBACK BOT - ДИАГНОСТИКА")
    print("=" * 60)

    # Проверки
    checks = [
        ("Настройки", check_settings),
        ("API Wildberries", check_wb_api),
        ("ИИ генератор", check_ai),
        ("Система", check_system),
        ("Бот", check_bot_status)
    ]

    results = []

    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Ошибка при проверке {check_name}: {e}")
            results.append((check_name, False))

    # Итоговый отчет
    print_section("📊 ИТОГОВЫЙ ОТЧЕТ")

    successful_checks = sum(1 for _, result in results if result)
    total_checks = len(results)

    print(f"✅ Успешных проверок: {successful_checks}/{total_checks}")

    for check_name, result in results:
        status = "✅ ПРОЙДЕНА" if result else "❌ НЕ ПРОЙДЕНА"
        print(f"   {status} - {check_name}")

    if successful_checks == total_checks:
        print("\n🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ НОРМАЛЬНО!")
        print("   Бот готов к автоматической работе с отзывами")
    else:
        print(f"\n⚠️  Найдены проблемы в {total_checks - successful_checks} проверках")
        print("   Проверьте настройки в .env файле")

    print("\n💡 СОВЕТЫ:")
    print("   - Для запуска бота: python main.py")
    print("   - Для тестирования: python scripts/test_bot.py")
    print("   - Для быстрой проверки: python check.py")

if __name__ == "__main__":
    main()
