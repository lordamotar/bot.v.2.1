from aiogram import types, Bot
from database import Database
from keyboards import (
    get_main_keyboard, 
    get_admin_keyboard,
    get_pending_chats_keyboard,
    get_active_chats_keyboard,
    get_managers_list_keyboard
)
import logging

logger = logging.getLogger(__name__)

async def handle_admin_panel(message: types.Message, db: Database):
    """Обработчик для открытия панели администратора"""
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь администратором
    if not db.is_admin(user_id):
        await message.answer(
            "У вас нет прав доступа к панели администратора",
            reply_markup=get_main_keyboard()
        )
        return
    
    await message.answer(
        "Панель администратора. Выберите действие:",
        reply_markup=get_admin_keyboard()
    )

async def handle_admin_stats(message: types.Message, db: Database):
    """Обработчик для отображения статистики"""
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь администратором
    if not db.is_admin(user_id):
        return
    
    stats = db.get_dashboard_stats()
    
    await message.answer(
        f"📊 *Статистика системы:*\n\n"
        f"👨‍💼 Менеджеры: {stats['total_managers']}\n"
        f"✅ Доступно менеджеров: {stats['available_managers']}\n"
        f"⏳ Ожидающих чатов: {stats['pending_chats']}\n"
        f"💬 Активных чатов: {stats['active_chats']}\n",
        parse_mode="Markdown",
        reply_markup=get_admin_keyboard()
    )

async def handle_admin_pending_chats(message: types.Message, db: Database):
    """Обработчик для отображения ожидающих чатов"""
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь администратором
    if not db.is_admin(user_id):
        return
    
    pending_chats = db.get_pending_chats()
    
    if not pending_chats:
        await message.answer(
            "В настоящее время нет ожидающих чатов",
            reply_markup=get_admin_keyboard()
        )
        return
    
    await message.answer(
        f"Найдено {len(pending_chats)} ожидающих чатов. Выберите чат для принятия:",
        reply_markup=get_pending_chats_keyboard(pending_chats)
    )

async def handle_admin_active_chats(message: types.Message, db: Database):
    """Обработчик для отображения активных чатов"""
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь администратором
    if not db.is_admin(user_id):
        return
    
    active_chats = db.get_all_active_chats()
    
    if not active_chats:
        await message.answer(
            "В настоящее время нет активных чатов",
            reply_markup=get_admin_keyboard()
        )
        return
    
    formatted_chats = []
    
    for chat in active_chats:
        client_id, username, client_name, client_phone, manager_id = chat
        manager_name = db.get_manager_name(manager_id) or f"ID: {manager_id}"
        
        formatted_chats.append((
            client_id, 
            username, 
            f"{client_name or username} (Менеджер: {manager_name})", 
            client_phone
        ))
    
    await message.answer(
        f"Найдено {len(active_chats)} активных чатов:",
        reply_markup=get_active_chats_keyboard(formatted_chats)
    )

async def handle_admin_managers(message: types.Message, db: Database):
    """Обработчик для отображения списка менеджеров"""
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь администратором
    if not db.is_admin(user_id):
        return
    
    managers = db.get_all_managers()
    
    if not managers:
        await message.answer(
            "В системе не найдено менеджеров",
            reply_markup=get_admin_keyboard()
        )
        return
    
    await message.answer(
        f"Найдено {len(managers)} менеджеров:",
        reply_markup=get_managers_list_keyboard(managers)
    )

async def handle_admin_take_chat(message: types.Message, bot: Bot, db: Database):
    """Обработчик для принятия чата администратором"""
    user_id = message.from_user.id
    admin_name = message.from_user.first_name or "Администратор"
    
    # Проверяем, является ли пользователь администратором
    if not db.is_admin(user_id):
        return
    
    # Извлекаем имя клиента из текста кнопки
    text = message.text
    if not text.startswith("Взять чат с "):
        await message.answer(
            "Неверный формат команды",
            reply_markup=get_admin_keyboard()
        )
        return
    
    client_info = text.replace("Взять чат с ", "")
    
    # Ищем клиента по имени и телефону
    pending_chats = db.get_pending_chats()
    target_client_id = None
    
    for chat in pending_chats:
        client_id, username, client_name, client_phone, _ = chat
        display_name = client_name if client_name else username
        display_text = f"{display_name}"
        if client_phone:
            display_text += f" ({client_phone})"
        
        if display_text == client_info:
            target_client_id = client_id
            break
    
    if not target_client_id:
        await message.answer(
            "Клиент не найден или чат уже был принят другим менеджером",
            reply_markup=get_admin_keyboard()
        )
        return
    
    # Принимаем чат
    if db.activate_chat(target_client_id, user_id):
        # Увеличиваем счетчик активных чатов администратора
        db.increment_manager_active_chats(user_id)
        
        # Обновляем активность администратора
        db.update_manager_activity(user_id)
        
        # Уведомляем клиента о подключении администратора
        await bot.send_message(
            target_client_id,
            "Администратор подключился к чату. Вы можете задать ваш вопрос."
        )
        
        # Отправляем автоматическое приветствие от имени администратора
        greeting_message = f"Здравствуйте! Меня зовут {admin_name}, я администратор поддержки. Чем могу вам помочь?"
        await bot.send_message(
            target_client_id,
            greeting_message
        )
        
        # Сохраняем приветственное сообщение в истории
        db.save_message(target_client_id, user_id, greeting_message, 'text')
        
        # Уведомляем администратора
        from keyboards import get_extended_chat_keyboard
        await message.answer(
            "Вы подключились к чату с клиентом.",
            reply_markup=get_extended_chat_keyboard()
        )
    else:
        await message.answer(
            "Не удалось подключиться к чату",
            reply_markup=get_admin_keyboard()
        ) 