import logging
import os
from datetime import datetime

def setup_logging():
    """Настройка логирования"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Файловый обработчик
    file_handler = logging.FileHandler(
        f"{log_dir}/bot_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Настройка root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )

def get_logger(name: str) -> logging.Logger:
    """Возвращает логгер"""
    return logging.getLogger(name)
