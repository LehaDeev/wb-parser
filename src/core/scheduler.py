import schedule
import time
import signal
import sys
from src.config.settings import settings
from .manager import ResponseManager

class BotScheduler:
    """Планировщик задач бота"""

    def __init__(self):
        self.shutdown = False
        self.manager = ResponseManager(test_mode=settings.TEST_MODE)

        # Обработчики сигналов
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Обработчик сигналов завершения"""
        print(f"\n🛑 Получен сигнал {signum}. Завершение работы...")
        self.shutdown = True

    def job(self):
        """Задача для планировщика"""
        if self.shutdown:
            return

        try:
            self.manager.process_new_reviews()
        except Exception as e:
            print(f"💥 Ошибка в задании: {e}")

    def run(self):
        """Запускает планировщик"""
        print("🚀 Запуск Wildberries Feedback Bot")
        print(f"🔧 Режим: {'ТЕСТОВЫЙ' if settings.TEST_MODE else 'РАБОЧИЙ'}")
        print(f"⏰ Проверка каждые {settings.CHECK_INTERVAL} минут")
        print("Для остановки нажмите Ctrl+C")
        print("-" * 50)

        # Первый запуск
        print("🎯 Первоначальный запуск...")
        self.job()

        # Настройка расписания
        schedule.every(settings.CHECK_INTERVAL).minutes.do(self.job)
        print("⏰ Планировщик запущен. Следующая проверка по расписанию.")

        # Основной цикл
        while not self.shutdown:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Ошибка в основном цикле: {e}")
                time.sleep(60)

        print("👋 Работа бота завершена.")
