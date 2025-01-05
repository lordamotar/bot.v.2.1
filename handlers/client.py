from aiogram import types, Bot
from aiogram.filters import Command
from database import Database
from keyboards import get_main_keyboard, get_chat_keyboard

async def handle_start(message: types.Message):
    await message.answer(
        "Добро пожаловать в службу поддержки! Чтобы начать чат с менеджером, "
        "нажмите кнопку ниже.",
        reply_markup=get_main_keyboard()
    )

async def handle_support_request(message: types.Message, bot: Bot, db: Database, manager_id: int):
    client_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    if db.is_client_in_active_chat(client_id):
        await message.answer("У вас уже есть активный чат с менеджером.")
        return

    # Создаем новый чат в БД
    db.create_chat(client_id, username)

    # Уведомляем клиента
    await message.answer(
        "Мы уведомили менеджера. Пожалуйста, дождитесь ответа.",
        reply_markup=get_chat_keyboard()
    )

    # Уведомляем менеджера
    from keyboards import get_manager_keyboard
    await bot.send_message(
        manager_id,
        f"Новый запрос от клиента @{username}: нажмите 'Принять чат', чтобы начать общение.",
        reply_markup=get_manager_keyboard(username)
    ) 