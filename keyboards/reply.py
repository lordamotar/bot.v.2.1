from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Контакты")],
            [KeyboardButton(text="Связаться с менеджером")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_cities_keyboard(cities: list[str]) -> ReplyKeyboardMarkup:
    """Клавиатура со списком городов в два столбца"""
    # Создаем список кнопок по два города в строке
    keyboard = []
    for i in range(0, len(cities), 2):
        row = []
        row.append(KeyboardButton(text=cities[i]))
        if i + 1 < len(cities):  # Проверяем, есть ли второй город для строки
            row.append(KeyboardButton(text=cities[i + 1]))
        keyboard.append(row)

    # Добавляем кнопку "Назад" отдельной строкой
    keyboard.append([KeyboardButton(text="Назад")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


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


def get_streets_keyboard(streets: list[str]) -> ReplyKeyboardMarkup:
    """Клавиатура со списком улиц в два столбца"""
    # Создаем список кнопок по две улицы в строке
    keyboard = []
    for i in range(0, len(streets), 2):
        row = []
        row.append(KeyboardButton(text=streets[i]))
        if i + 1 < len(streets):  # Проверяем, есть ли вторая улица для строки
            row.append(KeyboardButton(text=streets[i + 1]))
        keyboard.append(row)

    # Добавляем кнопку "Назад к городам" отдельной строкой
    keyboard.append([KeyboardButton(text="Назад к городам")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
