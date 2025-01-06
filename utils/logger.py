import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime


def setup_logger():
    # Создаем директорию для логов, если её нет
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Настраиваем формат логирования
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)

    # Создаем файл лога с текущей датой
    current_date = datetime.now().strftime('%Y-%m-%d')
    file_handler = RotatingFileHandler(
        f'logs/bot_{current_date}.log',
        maxBytes=5242880,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # Настраиваем корневой логгер
    logger = logging.getLogger('bot')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
