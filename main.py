import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import load_config
from database import Database
from handlers.client import handle_start, handle_support_request
from handlers.manager import handle_accept_chat
from handlers.common import handle_close_chat, handle_message
from handlers.contacts import (
    handle_contacts,
    handle_back,
    handle_city_selection,
    handle_back_to_cities,
    handle_street_selection
)
from utils.logger import logger

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка конфигурации
config = load_config()
bot = Bot(token=config.config.token)
dp = Dispatcher()
db = Database(config.db.database)


# Регистрация хендлеров
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await handle_start(message)


@dp.message(lambda message: message.text == "Контакты")
async def contacts(message: types.Message):
    await handle_contacts(message, db)


@dp.message(lambda message: message.text == "Назад")
async def back(message: types.Message):
    await handle_back(message)


@dp.message(lambda message: message.text == "Назад к городам")
async def back_to_cities(message: types.Message):
    await handle_back_to_cities(message, db)


@dp.message(lambda message: message.text in db.get_all_cities())
async def city_selected(message: types.Message):
    await handle_city_selection(message, db)


@dp.message(lambda message: message.text == "Связаться с менеджером")
async def request_support(message: types.Message):
    await handle_support_request(message, bot, db, config.config.manager_id)


@dp.message(lambda message: message.text.startswith("Принять чат"))
async def accept_chat(message: types.Message):
    await handle_accept_chat(message, bot, db, config.config.manager_id)


@dp.message(lambda message: message.text == "Завершить чат")
async def close_chat(message: types.Message):
    await handle_close_chat(message, bot, db, config.config.manager_id)


@dp.message(lambda message: message.text in [street for city_id in range(1, 18)
           for street in db.get_streets_by_city(city_id)])
async def street_selected(message: types.Message):
    await handle_street_selection(message, db)


# Общий обработчик должен быть последним
@dp.message()
async def handle_messages(message: types.Message):
    await handle_message(message, bot, db, config.config.manager_id)


async def main():
    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        logger.info("Starting bot...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print('Бот выключен')
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
