from aiogram import types
from database import Database
from keyboards import get_cities_keyboard, get_main_keyboard, get_streets_keyboard
from utils.logger import logger


async def handle_contacts(message: types.Message, db: Database):
    """Обработка кнопки Контакты"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    logger.info(f"User {username} (ID: {user_id}) requested contacts")
    
    cities = db.get_all_cities()
    await message.answer(
        "Выберите город:",
        reply_markup=get_cities_keyboard(cities)
    )


async def handle_city_selection(message: types.Message, db: Database):
    """Обработка выбора города"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    city = message.text
    
    logger.info(f"User {username} (ID: {user_id}) selected city: {city}")
    
    cities = db.get_all_cities()
    if city in cities:
        city_id = cities.index(city) + 1
        streets = db.get_streets_by_city(city_id)
        if streets:
            logger.info(f"Found {len(streets)} streets for city {city}")
            await message.answer(
                f"Выберите улицу в городе {city}:",
                reply_markup=get_streets_keyboard(streets)
            )
        else:
            logger.warning(f"No streets found for city {city}")
            await message.answer(
                f"В городе {city} пока нет добавленных улиц.",
                reply_markup=get_cities_keyboard(cities)
            )


async def handle_back(message: types.Message):
    """Обработка кнопки Назад"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    logger.info(f"User {username} (ID: {user_id}) returned to main menu")
    
    await message.answer(
        "Главное меню",
        reply_markup=get_main_keyboard()
    )


async def handle_back_to_cities(message: types.Message, db: Database):
    """Обработка кнопки Назад к городам"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    logger.info(f"User {username} (ID: {user_id}) returned to cities list")
    
    await handle_contacts(message, db) 