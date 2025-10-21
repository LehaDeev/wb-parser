#!/usr/bin/env python3
"""
Скрипт для отправки ежедневного отчета
"""

import os
import sys
from datetime import datetime

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api.wb_client import WBAPIClient
from src.utils.telegram_notifier import TelegramNotifier

def main():
    print("📊 Отправка ежедневного отчета Wildberries Bot...")

    try:
        # Получаем статистику
        client = WBAPIClient(test_mode=False)
        stats = client.get_unanswered_count()

        print(f"📈 Статистика получена: {stats.get('countUnanswered', 0)} неотвеченных отзывов")

        # Отправляем отчет
        telegram = TelegramNotifier()
        if telegram.enabled:
            daily_stats = {
                'date': datetime.now().strftime('%d.%m.%Y'),
                'checks_today': 'N/A',
                'reviews_processed': 'N/A',
                'replies_sent': 'N/A',
                'unanswered': stats.get('countUnanswered', 0),
                'new_today': stats.get('countUnansweredToday', 0),
                'avg_rating': stats.get('valuation', 'N/A')
            }
            telegram.notify_daily_statistics(daily_stats)
            print('✅ Ежедневный отчет отправлен в Telegram')
        else:
            print('⚠️ Telegram не настроен, отчет не отправлен')

    except Exception as e:
        print(f'❌ Ошибка отправки отчета: {e}')
        sys.exit(1)

if __name__ == "__main__":
    main()
