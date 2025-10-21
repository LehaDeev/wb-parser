#!/usr/bin/env python3
"""
Wildberries Feedback Bot для GitHub Actions
"""

import os
import sys
import time
from datetime import datetime

def main():
    print("🚀 Wildberries Feedback Bot - GitHub Actions")
    print(f"🕒 Время запуска: {datetime.now()}")
    print(f"🔧 Режим: {'ТЕСТОВЫЙ' if os.getenv('TEST_MODE') == 'true' else 'РАБОЧИЙ'}")

    try:
        from src.core.manager import ResponseManager

        # Создаем менеджер и запускаем одну итерацию
        manager = ResponseManager(test_mode=False)
        manager.process_new_reviews()

        print("✅ Обработка завершена успешно")
        return 0

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
