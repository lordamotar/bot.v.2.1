import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import load_config
from database import Database
from handlers.client import handle_start, handle_support_request
from handlers.manager import handle_accept_chat
from handlers.common import handle_close_chat, handle_message

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

@dp.message(lambda message: message.text == "Связаться с менеджером")
async def request_support(message: types.Message):
    await handle_support_request(message, bot, db, config.config.manager_id)

@dp.message(lambda message: message.text.startswith("Принять чат"))
async def accept_chat(message: types.Message):
    await handle_accept_chat(message, bot, db, config.config.manager_id)

@dp.message(lambda message: message.text == "Завершить чат")
async def close_chat(message: types.Message):
    await handle_close_chat(message, bot, db, config.config.manager_id)

@dp.message()
async def handle_messages(message: types.Message):
    await handle_message(message, bot, db, config.config.manager_id)

async def main():
    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
