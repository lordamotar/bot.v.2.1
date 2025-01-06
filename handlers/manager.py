from aiogram import types, Bot
from database import Database
from keyboards import get_chat_keyboard, get_main_keyboard


async def handle_accept_chat(message: types.Message, bot: Bot, db: Database, manager_id: int):
    if message.from_user.id != manager_id:
        return

    # Получаем username клиента из текста кнопки
    username = message.text.replace("Принять чат с ", "")

    # Находим чат в БД и активируем его
    client_id = db.get_client_id_by_username(username)
    if client_id:
        db.activate_chat(client_id, manager_id)
        await bot.send_message(
            client_id,
            "Менеджер подключился к чату. Вы можете задать ваш вопрос.",
            reply_markup=get_chat_keyboard()
        )
        await message.answer(
            f"Вы подключились к чату с клиентом {username}",
            reply_markup=get_chat_keyboard()
        )
    else:
        await message.answer("Не удалось найти чат с указанным пользователем")
