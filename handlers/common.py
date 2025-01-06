from aiogram import types, Bot
from database import Database
from keyboards import get_main_keyboard


async def handle_close_chat(message: types.Message, bot: Bot, db: Database, manager_id: int):
    user_id = message.from_user.id

    # Если это менеджер, найдем активный чат с клиентом
    if user_id == manager_id:
        active_chat = db.get_active_chat(user_id)
        if active_chat:
            client_id = active_chat[0]  # client_id из БД
            db.close_chat(client_id)

            # Уведомляем клиента
            await bot.send_message(
                client_id,
                "Менеджер завершил чат. Если у вас есть еще вопросы, вы можете связаться с нами снова.",
                reply_markup=get_main_keyboard()
            )
            # Уведомляем менеджера
            await message.answer(
                "Чат завершен.",
                reply_markup=get_main_keyboard()
            )
    else:
        # Если это клиент
        if db.close_chat(user_id):
            await message.answer(
                "Спасибо за обращение! Если у вас есть еще вопросы, вы можете связаться с нами снова.",
                reply_markup=get_main_keyboard()
            )
            await bot.send_message(
                manager_id,
                f"Клиент завершил чат.",
                reply_markup=get_main_keyboard()
            )


async def handle_message(message: types.Message, bot: Bot, db: Database, manager_id: int):
    user_id = message.from_user.id

    if user_id == manager_id:
        # Если пишет менеджер, найдем активный чат
        active_chat = db.get_active_chat(manager_id)
        if active_chat:
            client_id = active_chat[0]  # client_id из БД
            await bot.send_message(client_id, message.text)
        else:
            await message.answer("У вас нет активного чата с клиентом")
    else:
        # Если пишет клиент
        if db.is_client_in_active_chat(user_id):
            await bot.send_message(manager_id, message.text)
        else:
            await message.answer(
                "У вас нет активного чата с менеджером. Нажмите 'Связаться с менеджером', чтобы начать чат.",
                reply_markup=get_main_keyboard()
            )
