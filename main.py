import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import load_config
from database import Database
from handlers.client import (
    handle_start, 
    handle_support_request, 
    handle_chat_history, 
    handle_view_media,
    handle_rating,
    handle_rating_comment,
    handle_share_contact,
    process_contact_data
)
from handlers.manager import (
    handle_accept_chat, 
    handle_manager_status, 
    handle_set_availability
)
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

# Инициализация менеджеров
for manager_id in config.config.managers:
    db.add_manager(manager_id)

# Устанавливаем администратора, если есть
if config.config.admin_manager_id:
    db.add_manager(config.config.admin_manager_id, is_admin=True)


# Регистрация хендлеров
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await handle_start(message, config, db)


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
    await handle_support_request(message, bot, db, config)


@dp.message(lambda message: message.text == "Поделиться контактом")
async def share_contact(message: types.Message):
    await handle_share_contact(message, bot, db, config)


@dp.message(lambda message: message.contact is not None)
async def contact_handler(message: types.Message):
    await process_contact_data(message, bot, db, config)


@dp.message(lambda message: message.text.startswith("Принять чат"))
async def accept_chat(message: types.Message):
    await handle_accept_chat(message, bot, db, config.config.managers)


@dp.message(lambda message: message.text == "Завершить чат")
async def close_chat(message: types.Message):
    await handle_close_chat(message, bot, db, config)


@dp.message(lambda message: message.text == "История сообщений")
async def chat_history(message: types.Message):
    await handle_chat_history(message, db)


@dp.message(lambda message: message.text.startswith("/view_"))
async def view_media(message: types.Message):
    await handle_view_media(message, db, bot)


@dp.message(lambda message: message.text.startswith("Оценка: "))
async def rate_chat(message: types.Message):
    await handle_rating(message, db)


@dp.message(lambda message: message.text in [street for city_id in range(1, 18)
           for street in db.get_streets_by_city(city_id)])
async def street_selected(message: types.Message):
    await handle_street_selection(message, db)


@dp.message(lambda message: message.text == "Пропустить" or 
            (db.get_chat_rating(message.from_user.id) is not None and 
             not message.text.startswith("Оценка: ") and
             not message.text.startswith("/") and
             not db.is_client_in_active_chat(message.from_user.id)))
async def add_rating_comment(message: types.Message):
    await handle_rating_comment(message, db)


@dp.message(lambda message: message.text == "Главное меню")
async def main_menu(message: types.Message):
    await handle_start(message, config, db)


# Общий обработчик должен быть последним
@dp.message()
async def handle_messages(message: types.Message):
    await handle_message(message, bot, db, config)


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
