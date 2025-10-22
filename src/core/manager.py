import time
from datetime import datetime
from src.api.wb_client import WBAPIClient
from src.ai.generator import AIGenerator
from .processor import ReviewProcessor
from src.utils.telegram_notifier import TelegramNotifier

class ResponseManager:
    """Менеджер обработки отзывов"""

    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.wb_client = WBAPIClient(test_mode=test_mode)
        self.ai_generator = AIGenerator(test_mode=test_mode)
        self.processor = ReviewProcessor(self.ai_generator)
        self.telegram = TelegramNotifier()

        # Статистика за день
        self.daily_stats = {
            'checks_count': 0,
            'reviews_processed': 0,
            'replies_sent': 0,
            'last_check_date': datetime.now().date()
        }

    def process_new_reviews(self):
        """Обрабатывает новые отзывы"""
        print("\n" + "="*60)
        print(f"🕒 Запуск обработки отзывов")
        print(f"🔧 Режим: {'ТЕСТОВЫЙ' if self.test_mode else 'РАБОЧИЙ'}")
        print("="*60)

        start_time = datetime.now()
        current_date = datetime.now().date()

        # Сброс статистики если новый день
        if current_date != self.daily_stats['last_check_date']:
            self._send_daily_report()  # Отправляем отчет за предыдущий день
            self.daily_stats = {
                'checks_count': 0,
                'reviews_processed': 0,
                'replies_sent': 0,
                'last_check_date': current_date
            }

        self.daily_stats['checks_count'] += 1

        try:
            # Получаем статистику
            wb_stats = {}
            if not self.test_mode:
                wb_stats = self.wb_client.get_unanswered_count()
                print(f"📊 Статистика: {wb_stats.get('countUnanswered', 0)} неотвеченных отзывов")
                print(f"📊 Новых сегодня: {wb_stats.get('countUnansweredToday', 0)}")
                print(f"⭐ Средняя оценка: {wb_stats.get('valuation', 'N/A')}")

            # Получаем отзывы
            reviews = self.wb_client.get_unanswered_reviews()

            if not reviews:
                print("📭 Неотвеченных отзывов не найдено.")
                return

            # Обрабатываем отзывы
            results = self.processor.process_reviews(reviews)
            self.daily_stats['reviews_processed'] += len(reviews)

            # Отправляем ответы и уведомления
            sent_count = self._send_replies(results)
            self.daily_stats['replies_sent'] += sent_count

            print(f"\n📊 ИТОГО: Обработано {sent_count} из {len(reviews)} отзывов")

        except Exception as e:
            error_msg = f"Критическая ошибка: {e}"
            print(f"💥 {error_msg}")
            self.telegram.notify_error(error_msg)

    def _send_replies(self, results: list) -> int:
        """Отправляет ответы и уведомляет в Telegram"""
        sent_count = 0

        for result in results:
            if result["success"] and not self.test_mode:
                time.sleep(0.5)  # Задержка между запросами

                success = self.wb_client.post_reply_to_review(
                    result["review"].id,
                    result["reply"]
                )

                if success:
                    sent_count += 1
                    print(f"✅ Ответ отправлен для отзыва {result['review'].id}")

                    # Отправляем уведомление о КАЖДОМ новом ответе
                    review_data = {
                    'user_name': result['review'].user_name,
                    'rating': result['review'].rating,
                    'product_name': result['review'].product_name,
                    'text': result['review'].review_text,
                    'time': datetime.now().strftime('%H:%M:%S')
                }
                    self.telegram.notify_new_review(review_data, result["reply"])

                else:
                    print(f"❌ Ошибка отправки ответа для отзыва {result['review'].id}")

        return sent_count

    def _send_daily_report(self):
        """Отправляет ежедневный отчет"""
        if self.test_mode or not self.telegram.enabled:
            return

        try:
            # Получаем текущую статистику для отчета
            wb_stats = self.wb_client.get_unanswered_count()

            daily_stats = {
                'date': self.daily_stats['last_check_date'].strftime('%d.%m.%Y'),
                'checks_today': self.daily_stats['checks_count'],
                'reviews_processed': self.daily_stats['reviews_processed'],
                'replies_sent': self.daily_stats['replies_sent'],
                'unanswered': wb_stats.get('countUnanswered', 0),
                'new_today': wb_stats.get('countUnansweredToday', 0),
                'avg_rating': wb_stats.get('valuation', 'N/A')
            }

            # Отправляем только если были проверки за день
            if self.daily_stats['checks_count'] > 0:
                self.telegram.notify_daily_statistics(daily_stats)
                print(f"📊 Отправлен ежедневный отчет за {daily_stats['date']}")

        except Exception as e:
            print(f"❌ Ошибка отправки ежедневного отчета: {e}")

    def __del__(self):
        """Деструктор - отправляет отчет при завершении"""
        if not self.test_mode:
            self._send_daily_report()
