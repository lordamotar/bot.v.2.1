from aiogram import types, Bot
from database import Database
from keyboards import get_main_keyboard, get_rating_keyboard, get_chat_keyboard
from handlers.client import handle_rate_chat_request
import logging

logger = logging.getLogger(__name__)


async def handle_close_chat(message: types.Message, bot: Bot, db: Database, config):
    user_id = message.from_user.id

    # Если это менеджер
    if user_id in config.config.managers:
        active_chat = db.get_active_chat(user_id)
        if active_chat:
            client_id = active_chat[0]  # client_id из БД
            db.close_chat(client_id)
            
            # Уменьшаем счетчик активных чатов менеджера
            db.decrement_manager_active_chats(user_id)

            # Уведомляем клиента
            await bot.send_message(
                client_id,
                "Менеджер завершил чат. Если у вас есть еще вопросы, вы можете связаться с нами снова.",
                reply_markup=get_main_keyboard()
            )
            
            # Предлагаем оценить чат
            await bot.send_message(
                client_id,
                "Пожалуйста, оцените качество обслуживания:",
                reply_markup=get_rating_keyboard()
            )
            
            # Уведомляем менеджера
            await message.answer(
                "Чат завершен.",
                reply_markup=get_main_keyboard()
            )
    else:
        # Если это клиент
        active_chat = db.get_active_chat_by_client_id(user_id)
        if active_chat and db.close_chat(user_id):
            manager_id = active_chat[1]  # manager_id из БД
            
            # Уменьшаем счетчик активных чатов менеджера, если менеджер назначен
            if manager_id:
                db.decrement_manager_active_chats(manager_id)
            
            await message.answer(
                "Спасибо за обращение! Если у вас есть еще вопросы, вы можете связаться с нами снова.",
                reply_markup=get_main_keyboard()
            )
            
            # Предлагаем оценить чат
            await handle_rate_chat_request(message, db)
            
            # Уведомляем менеджера
            if manager_id:
                await bot.send_message(
                    manager_id,
                    "Клиент завершил чат.",
                    reply_markup=get_main_keyboard()
                )
        else:
            await message.answer(
                "У вас нет активного чата.",
                reply_markup=get_main_keyboard()
            )


async def handle_message(message: types.Message, bot: Bot, db: Database, config):
    user_id = message.from_user.id
    is_manager = user_id in config.config.managers

    # Определяем тип сообщения и извлекаем необходимые данные
    message_type = 'text'
    file_id = None
    content = message.text or ""
    
    # Проверка на медиафайлы и стикеры - функция отключена
    content_type = message.content_type
    if content_type != 'text':
        # Уведомляем пользователя, что отправка медиафайлов отключена
        await message.answer(
            "Отправка медиафайлов в данный момент отключена. Пожалуйста, отправьте только текстовое сообщение.",
            reply_markup=get_chat_keyboard() if db.is_client_in_active_chat(user_id) else get_main_keyboard()
        )
        logger.info(f"Blocked media message from user {user_id}, content_type: {content_type}")
        return
    
    # Продолжаем обработку только текстовых сообщений
    logger.info(f"Processing text message from user {user_id}")
        
    if is_manager:
        # Обновляем активность менеджера
        db.update_manager_activity(user_id)
        
        # Если пишет менеджер, найдем активный чат
        active_chat = db.get_active_chat(user_id)
        if active_chat:
            client_id = active_chat[0]  # client_id из БД
            
            try:
                # Сохраняем сообщение в историю
                saved = db.save_message(client_id, user_id, content, message_type, file_id)
                if saved:
                    logger.info(f"Manager message saved: chat_id={client_id}, sender_id={user_id}")
                else:
                    logger.error(f"Failed to save manager message: chat_id={client_id}")
            except Exception as e:
                logger.error(f"Error saving manager message: {e}")
            
            # Отправляем сообщение клиенту
            try:
                await bot.send_message(client_id, content)
                logger.info(f"Text message sent to client {client_id} successfully")
            except Exception as e:
                logger.error(f"Error sending text to client {client_id}: {e}")
                await message.answer(
                    "Произошла ошибка при отправке сообщения клиенту.",
                    reply_markup=get_chat_keyboard()
                )
        else:
            await message.answer("У вас нет активного чата с клиентом")
    else:
        # Если пишет клиент
        if db.is_client_in_active_chat(user_id):
            # Получаем информацию о чате
            active_chat = db.get_active_chat_by_client_id(user_id)
            if not active_chat or not active_chat[1]:  # Проверяем, назначен ли менеджер
                await message.answer(
                    "Ваш запрос еще не принят менеджером. Пожалуйста, ожидайте.",
                    reply_markup=get_chat_keyboard()
                )
                return
                
            manager_id = active_chat[1]
            
            try:
                # Сохраняем сообщение в историю с правильным ID отправителя
                saved = db.save_message(user_id, user_id, content, message_type, file_id)
                if saved:
                    logger.info(f"Client message saved: chat_id={user_id}, sender_id={user_id}")
                else:
                    logger.error(f"Failed to save client message: chat_id={user_id}")
            except Exception as e:
                logger.error(f"Error saving client message: {e}")
            
            # Отмечаем все предыдущие сообщения как прочитанные
            db.mark_messages_as_read(user_id, user_id)
            
            # Отправляем сообщение менеджеру
            try:
                await bot.send_message(manager_id, content)
                logger.info(f"Text message sent to manager {manager_id} successfully")
            except Exception as e:
                logger.error(f"Error sending text to manager {manager_id}: {e}")
                await message.answer(
                    "Произошла ошибка при отправке сообщения менеджеру. Пожалуйста, попробуйте еще раз.",
                    reply_markup=get_chat_keyboard()
                )
        else:
            await message.answer(
                "У вас нет активного чата с менеджером. Нажмите 'Связаться с менеджером', чтобы начать чат.",
                reply_markup=get_main_keyboard()
            )
