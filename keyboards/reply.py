from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Связаться с менеджером")]],
        resize_keyboard=True
    )
    return keyboard


def get_chat_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Завершить чат")]],
        resize_keyboard=True
    )
    return keyboard


def get_manager_keyboard(username: str) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=f"Принять чат с {username}")]],
        resize_keyboard=True
    )
    return keyboard 