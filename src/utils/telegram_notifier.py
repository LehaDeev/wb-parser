import os
import requests
import logging
from datetime import datetime

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.enabled = bool(self.bot_token and self.chat_id)

        if self.enabled:
            print("✅ Telegram уведомления включены")
        else:
            print("⚠️ Telegram уведомления отключены (не настроены токены)")

    def send_message(self, message: str):
        """Отправляет сообщение в Telegram"""
        if not self.enabled:
            return False

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }

            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200

        except Exception as e:
            print(f"❌ Ошибка отправки в Telegram: {e}")
            return False

    def notify_new_review(self, review_data: dict, reply_text: str):
        """Уведомление о новом ответе на отзыв"""
        if not self.enabled:
            return

        rating_emojis = "⭐" * review_data['rating']
        message = f"""
📝 <b>Новый ответ на отзыв</b>

👤 <b>Покупатель:</b> {review_data['user_name'] or 'Аноним'}
⭐ <b>Оценка:</b> {rating_emojis} ({review_data['rating']}/5)
🏷️ <b>Товар:</b> {review_data['product_name']}

💬 <b>Отзыв:</b>
{review_data['text'][:200]}{'...' if len(review_data['text']) > 200 else ''}

🤖 <b>Ответ бота:</b>
{reply_text[:300]}{'...' if len(reply_text) > 300 else ''}

🕒 <b>Время:</b> {review_data['time']}
        """.strip()

        self.send_message(message)

    def notify_daily_statistics(self, stats: dict):
        """Ежедневная статистика"""
        if not self.enabled:
            return

        message = f"""
📊 <b>Ежедневная статистика Wildberries Bot</b>

📅 <b>Дата:</b> {stats.get('date', '')}
🔄 <b>Проверок за день:</b> {stats.get('checks_today', 0)}
📝 <b>Обработано отзывов:</b> {stats.get('reviews_processed', 0)}
📤 <b>Отправлено ответов:</b> {stats.get('replies_sent', 0)}
⭐ <b>Текущая средняя оценка:</b> {stats.get('avg_rating', 'N/A')}

📈 <b>Неотвеченных отзывов:</b> {stats.get('unanswered', 0)}
📋 <b>Новых за сегодня:</b> {stats.get('new_today', 0)}

{'🎉 <b>Все отзывы обработаны!</b>' if stats.get('unanswered', 0) == 0 else '⚠️ <b>Есть неотвеченные отзывы</b>'}
        """.strip()

        self.send_message(message)

    def notify_error(self, error_message: str):
        """Уведомление об ошибке"""
        if not self.enabled:
            return

        message = f"""
🚨 <b>Ошибка Wildberries Bot</b>

❌ <b>Ошибка:</b>
{error_message}

🆘 <b>Требуется проверка!</b>
        """.strip()

        self.send_message(message)
