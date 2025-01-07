from aiogram import types, Bot
from aiogram.filters import Command
from database import Database
from keyboards import get_main_keyboard, get_chat_keyboard, get_manager_keyboard
import logging

logger = logging.getLogger(__name__)


async def handle_start(message: types.Message):
    await message.answer(
        "Добро пожаловать в службу поддержки! Чтобы начать чат с менеджером, "
        "нажмите кнопку ниже.",
        reply_markup=get_main_keyboard()
    )


async def handle_support_request(message: types.Message, bot: Bot, db: Database, manager_id: int):
    """Обработка запроса на связь с менеджером"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    # Проверяем наличие свободных менеджеров
    available_managers = db.get_available_managers_count()
    logger.info(f"Available managers: {available_managers}")

    if available_managers <= 0:
        await message.answer(
            "К сожалению, все менеджеры сейчас заняты. "
            "Пожалуйста, попробуйте обратиться чуть позже.",
            reply_markup=get_main_keyboard()
        )
        return

    # Проверяем, не находится ли пользователь уже в чате
    if db.is_client_in_active_chat(user_id):
        await message.answer(
            "У вас уже есть активный чат с менеджером.",
            reply_markup=get_chat_keyboard()
        )
        return

    # Создаем новый чат
    if db.create_chat(user_id, username):
        logger.info(f"Created chat for user {username} (ID: {user_id})")
        await message.answer(
            "Ваш запрос отправлен менеджеру. Пожалуйста, ожидайте ответа.",
            reply_markup=get_chat_keyboard()
        )
        # Уведомляем менеджера
        await bot.send_message(
            manager_id,
            f"Новый запрос в чат от пользователя {username}",
            reply_markup=get_manager_keyboard(username)
        )
    else:
        logger.error(f"Failed to create chat for user {username} (ID: {user_id})")
        await message.answer(
            "Произошла ошибка при создании чата. Пожалуйста, попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
