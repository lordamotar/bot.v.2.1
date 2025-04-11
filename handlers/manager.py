from aiogram import types, Bot
from database import Database
from keyboards import get_chat_keyboard, get_main_keyboard, get_manager_status_keyboard


async def handle_accept_chat(message: types.Message, bot: Bot, db: Database, managers_list: list):
    """Обработчик для принятия чата менеджером"""
    manager_id = message.from_user.id
    manager_name = message.from_user.first_name or "Менеджер"
    
    # Проверяем, является ли пользователь менеджером
    if manager_id not in managers_list:
        return

    # Извлекаем username клиента из текста кнопки
    # Формат "Принять чат с username (имя, телефон)" или "Принять чат с username"
    button_text = message.text
    username_part = button_text.replace("Принять чат с ", "")
    
    # Проверяем, содержит ли кнопка дополнительную информацию
    if "(" in username_part:
        username = username_part.split("(")[0].strip()
    else:
        username = username_part.strip()

    # Находим чат в БД и активируем его
    client_id = db.get_client_id_by_username(username)
    if not client_id:
        await message.answer("Не удалось найти чат с указанным пользователем")
        return
        
    # Проверяем, не занят ли уже чат другим менеджером
    if db.is_client_in_active_chat(client_id):
        active_chat = db.get_active_chat_by_client_id(client_id)
        if active_chat and active_chat[1] and active_chat[1] != manager_id:
            await message.answer(
                f"Этот чат уже принят другим менеджером.",
                reply_markup=get_main_keyboard()
            )
            return
    
    # Получаем имя клиента из контактной информации
    client_contact = db.get_client_contact_info(client_id)
    client_name = client_contact[0] if client_contact and client_contact[0] else username
    
    # Активируем чат и обновляем счетчики для менеджера
    if db.activate_chat(client_id, manager_id):
        # Увеличиваем счетчик активных чатов менеджера
        db.increment_manager_active_chats(manager_id)
        
        # Обновляем активность менеджера
        db.update_manager_activity(manager_id)
        
        # Уведомляем клиента о подключении менеджера
        await bot.send_message(
            client_id,
            "Менеджер подключился к чату. Вы можете задать ваш вопрос.",
            reply_markup=get_chat_keyboard()
        )
        
        # Отправляем автоматическое приветствие от имени менеджера
        greeting_message = f"Здравствуйте, {client_name}! Меня зовут {manager_name}. Чем могу вам помочь?"
        await bot.send_message(
            client_id,
            greeting_message,
            reply_markup=get_chat_keyboard()
        )
        
        # Сохраняем приветственное сообщение в истории
        db.save_message(client_id, manager_id, greeting_message, 'text')
        
        # Уведомляем менеджера
        await message.answer(
            f"Вы подключились к чату с клиентом {username}",
            reply_markup=get_chat_keyboard()
        )
        
        # Отправляем уведомление другим менеджерам, что чат уже занят
        for other_manager_id in managers_list:
            if other_manager_id != manager_id:
                try:
                    await bot.send_message(
                        other_manager_id,
                        f"Чат с пользователем {username} уже принят другим менеджером."
                    )
                except Exception:
                    pass  # Игнорируем ошибки при отправке уведомлений
    else:
        await message.answer("Не удалось подключиться к чату")


async def handle_manager_status(message: types.Message, db: Database):
    """Обработчик для управления статусом менеджера"""
    manager_id = message.from_user.id
    
    # Получаем статистику менеджера
    stats = db.get_manager_stats(manager_id)
    if not stats:
        await message.answer("Не удалось получить информацию о вашем статусе")
        return
        
    active_chats, total_chats, rating = stats
    
    await message.answer(
        f"🔹 Ваш статус:\n"
        f"• Активных чатов: {active_chats}\n"
        f"• Всего чатов: {total_chats}\n"
        f"• Средняя оценка: {rating:.1f}/5.0\n\n"
        f"Выберите действие:",
        reply_markup=get_manager_status_keyboard()
    )


async def handle_set_availability(message: types.Message, db: Database, available: bool):
    """Обработчик для установки доступности менеджера"""
    manager_id = message.from_user.id
    
    if db.set_manager_availability(manager_id, available):
        status = "доступен для новых чатов" if available else "недоступен для новых чатов"
        await message.answer(
            f"Ваш статус изменен. Теперь вы {status}.",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            "Не удалось изменить ваш статус",
            reply_markup=get_main_keyboard()
        )