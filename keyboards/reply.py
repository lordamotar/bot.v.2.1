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
        keyboard=[
            [KeyboardButton(text="История сообщений")],
            [KeyboardButton(text="Завершить чат")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_manager_keyboard(username: str, client_name: str = None, client_phone: str = None) -> ReplyKeyboardMarkup:
    # Формируем текст кнопки с информацией о клиенте
    button_text = f"Принять чат с {username}"
    if client_name and client_phone:
        button_text = f"Принять чат с {username} ({client_name}, {client_phone})"
    elif client_name:
        button_text = f"Принять чат с {username} ({client_name})"

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=button_text)]],
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


def get_rating_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для оценки чата"""
    keyboard = [
        [
            KeyboardButton(text="Оценка: 1"),
            KeyboardButton(text="Оценка: 2"),
            KeyboardButton(text="Оценка: 3"),
            KeyboardButton(text="Оценка: 4"),
            KeyboardButton(text="Оценка: 5"),
        ],
        [KeyboardButton(text="Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_manager_status_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для управления статусом менеджера"""
    keyboard = [
        [
            KeyboardButton(text="Доступен для чатов"),
            KeyboardButton(text="Недоступен для чатов")
        ],
        [KeyboardButton(text="Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_share_contact_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для запроса контактных данных"""
    keyboard = [
        [KeyboardButton(text="Поделиться контактом", request_contact=True)],
        [KeyboardButton(text="Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
