import sqlite3
from typing import Optional, List, Tuple
from utils.logger import logger
import threading


class Database:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self._local = threading.local()
        logger.info(f"Initializing database: {db_file}")
        self._create_tables()

    def _get_connection(self):
        """Получение соединения для текущего потока"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(self.db_file)
            self._local.cursor = self._local.connection.cursor()
        return self._local.connection, self._local.cursor

    def _create_tables(self):
        """Создание необходимых таблиц, если они еще не существуют"""
        conn, cursor = self._get_connection()
        try:
            # Создаем таблицы только если они не существуют
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    client_id INTEGER PRIMARY KEY,
                    manager_id INTEGER,
                    is_active BOOLEAN DEFAULT FALSE,
                    username TEXT,
                    client_name TEXT,
                    client_phone TEXT,
                    client_nickname TEXT
                )
            """)

            # Проверяем наличие полей client_name, client_phone, client_nickname в таблице chats
            cursor.execute("PRAGMA table_info(chats)")
            columns = {column[1] for column in cursor.fetchall()}
            
            # Если таблица chats существует, но нет нужных полей для хранения контактов
            if 'client_id' in columns and 'client_name' not in columns:
                logger.info("Обновление структуры таблицы chats, добавление полей для контактов...")
                # Добавляем недостающие поля
                try:
                    cursor.execute("ALTER TABLE chats ADD COLUMN client_name TEXT")
                    cursor.execute("ALTER TABLE chats ADD COLUMN client_phone TEXT")
                    cursor.execute("ALTER TABLE chats ADD COLUMN client_nickname TEXT")
                    conn.commit()
                    logger.info("Поля для контактных данных успешно добавлены в таблицу chats")
                except sqlite3.Error as e:
                    logger.error(f"Ошибка при добавлении полей в таблицу chats: {e}")
                    # Продолжаем выполнение, так как поля могут уже существовать

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS streets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    FOREIGN KEY (city_id) REFERENCES cities (id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    street_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    weekdays_time TEXT,
                    weekend_time TEXT,
                    contact TEXT,
                    geo_link TEXT,
                    category TEXT,
                    FOREIGN KEY (street_id) REFERENCES streets (id) ON DELETE CASCADE
                )
            """)

            # Проверяем, есть ли данные в таблице городов
            cursor.execute("SELECT COUNT(*) FROM cities")
            cities_count = cursor.fetchone()[0]

            # Заполняем начальные данные только если таблицы были только что созданы
            if cities_count == 0:
                # Заполняем таблицу городов
                cities = [
                    "Актобе", "Алматы", "Астана", "Атырау", "Караганда",
                    "Кокшетау", "Кызылорда", "Павлодар", "Петропавловск",
                    "Семей", "Степногорск", "Темиртау", "Туркестан",
                    "Уральск", "Усть-Каменогорск", "Шымкент", "Экибастуз"
                ]

                cursor.executemany(
                    "INSERT INTO cities (name) VALUES (?)",
                    [(city,) for city in cities]
                )

                # Список улиц с привязкой к городам
                streets_data = [
                    # Актобе
                    (1, "Проспект 312 Стрелковой Дивизии 3/2"),
                    # Алматы
                    (2, "проспект Рыскулова 103"),
                    (2, "улица Жандосова 2Б"),
                    (2, "микрорайон Аксай 1А 16Б"),
                    (2, "улица Васнецова 4/93"),
                    (2, "проспект Суюнбая 284"),
                    (2, "улица Бережинского 7"),
                    # Астана
                    (3, "улица Айнакол 111"),
                    (3, "улица Сакен Сейфуллин 11/1в"),
                    (3, "шоссе Алаш 42"),
                    # Атырау
                    (4, "Северная промышленная зона 45"),
                    # Караганда
                    (5, "134-й учетный квартал к2"),
                    (5, "улица Бытовая 17/1"),
                    # Кокшетау
                    (6, "улица Шокана Уалиханова 197"),
                    # Кызылорда
                    (7, "ул. Коркыт ата 125"),
                    (7, "улица Узакбая Караманова 103а"),
                    # Павлодар
                    (8, "Северная промышленная зона 190/1"),
                    (8, "улица Транспортная 17/9"),
                    (8, "улица Луначарского 44/2"),
                    # Петропавловск
                    (9, "улица Парковая 57Б"),
                    # Семей (исправленные записи)
                    (10, "трасса Семей-Павлодар 10"),
                    (10, "улица Кутжанова 23"),
                    (10, "улица Бозтаева 106"),
                    (10, "улица Красный Пильщик 36/2"),
                    # Степногорск
                    (11, "2-й микрорайон 77"),
                    # Темиртау
                    (12, "улица Мичурина 36"),
                    # Туркестан
                    (13, "улица Кудайбердинова 108А"),
                    # Уральск
                    (14, "микрорайон Северо-Восток 2 23/2"),
                    (14, "улица Поповича 12А"),
                    # Усть-Каменогорск
                    (15, "ул. Жибек Жолы 19"),
                    (15, "проспект Абая 160"),
                    (15, "улица Тракторная 24"),
                    (15, "проспект Абая 154/1"),
                    # Шымкент
                    (16, "ул. Аргынбекова 3"),
                    (16, "226-й квартал ст353"),
                    (16, "Тамерлановское шоссе 128/7"),
                    (16, "улица Жибек жолы 886"),
                    (16, "улица Пищевикова 6"),
                    # Экибастуз
                    (17, "улица Желтоксан 9")
                ]

                cursor.executemany(
                    "INSERT INTO streets (city_id, name) VALUES (?, ?)",
                    streets_data
                )

                # Получаем соответствие улиц и их id
                cursor.execute("SELECT id, name FROM streets")
                streets_mapping = {name: id for id, name in cursor.fetchall()}

                # Получаем соответствие улиц и городов
                cursor.execute("""
                    SELECT s.id, c.name
                    FROM streets s
                    JOIN cities c ON s.city_id = c.id
                """)
                street_city_mapping = {street_id: city_name for street_id, city_name in cursor.fetchall()}

                # Создаем список данных с правильными названиями городов
                items_data = [
                    (street_id, name, address, weekdays, weekend, contact, geo, category)
                    for street_id, name, address, weekdays, weekend, contact, geo, category in [
                        # Актобе
                        (streets_mapping["Проспект 312 Стрелковой Дивизии 3/2"],
                        street_city_mapping[streets_mapping["Проспект 312 Стрелковой Дивизии 3/2"]],
                        "Проспект 312 Стрелковой Дивизии 3/2",
                        "Пн-Пт: 09:00-18:00", "Сб: 09:00-14:00",
                        "7(705)752-33-07, 7(771)350-34-83", "https://go.2gis.com/zjq6q", "Магазин"),

                        # Алматы
                        (streets_mapping["проспект Рыскулова 103"],
                        street_city_mapping[streets_mapping["проспект Рыскулова 103"]],
                        "проспект Рыскулова 103",
                        "09:00-20:00", "Без выходных",
                        "7(705) 752-06-45", "https://go.2gis.com/9urut", "Магазин"),
                        (streets_mapping["улица Жандосова 2Б"],
                        street_city_mapping[streets_mapping["улица Жандосова 2Б"]],
                        "улица Жандосова 2Б",
                        "09:00-20:00", "Без выходных",
                        "7(771) 350-34-72", "https://go.2gis.com/4n01z", "Магазин"),
                        (streets_mapping["микрорайон Аксай 1А 16Б"],
                        street_city_mapping[streets_mapping["микрорайон Аксай 1А 16Б"]],
                        "микрорайон Аксай 1А 16Б",
                        "09:00-20:00", "Без выходных",
                        "7(705) 795-59-61", "https://go.2gis.com/vevjl", "Магазин"),
                        (streets_mapping["улица Васнецова 4/93"],
                        street_city_mapping[streets_mapping["улица Васнецова 4/93"]],
                        "улица Васнецова 4/93",
                        "09:00-20:00", "Без выходных",
                        "7(705) 798-34-17", "https://go.2gis.com/5bb53", "Магазин"),
                        (streets_mapping["проспект Суюнбая 284"],
                        street_city_mapping[streets_mapping["проспект Суюнбая 284"]],
                        "проспект Суюнбая 284",
                        "Пн-Пт: 09:00-18:00 (Обед: 13:00-14:00)", "Сб 09:00-14:00 Вс: Выходной",
                        "8(7272)90-28-22", "https://go.2gis.com/ilsyk", "Магазин"),
                        (streets_mapping["улица Бережинского 7"],
                        street_city_mapping[streets_mapping["улица Бережинского 7"]],
                        "улица Бережинского 7",
                        "Пн-Пт: 09:00-18:00", "Сб: 09:00-14:00 Вс: Выходной",
                        "7(705) 735-46-30", "https://go.2gis.com/klhyg", "Магазин"),

                        # И так далее для всех остальных улиц
                        # ...
                    ]
                ]

                # Вставляем данные в таблицу items
                cursor.executemany(
                    """
                    INSERT INTO items (street_id, name, address, weekdays_time, weekend_time, contact, geo_link, category)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    items_data
                )

            # Проверяем наличие таблицы messages
            cursor.execute("PRAGMA table_info(messages)")
            columns = {column[1] for column in cursor.fetchall()}
            
            # Если таблица messages существует, но не имеет нужных столбцов
            if 'id' in columns and 'message_type' not in columns:
                logger.info("Обновление структуры таблицы messages...")
                # Переименовываем старую таблицу
                cursor.execute("ALTER TABLE messages RENAME TO messages_old")
                
                # Создаем новую таблицу с нужной структурой
                cursor.execute("""
                    CREATE TABLE messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER NOT NULL,  
                        sender_id INTEGER NOT NULL,
                        message_text TEXT NOT NULL,
                        message_type TEXT DEFAULT 'text',
                        file_id TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        is_read BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (chat_id) REFERENCES chats (client_id) ON DELETE CASCADE
                    )
                """)
                
                # Переносим данные из старой таблицы в новую
                cursor.execute("""
                    INSERT INTO messages (id, chat_id, sender_id, message_text, timestamp, is_read)
                    SELECT id, chat_id, sender_id, message_text, timestamp, is_read
                    FROM messages_old
                """)
                
                # Удаляем старую таблицу
                cursor.execute("DROP TABLE messages_old")
                logger.info("Обновление структуры таблицы messages выполнено успешно")
            else:
                # Создаем таблицу для хранения истории сообщений, если её нет
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER NOT NULL,  
                        sender_id INTEGER NOT NULL,
                        message_text TEXT NOT NULL,
                        message_type TEXT DEFAULT 'text',
                        file_id TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        is_read BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (chat_id) REFERENCES chats (client_id) ON DELETE CASCADE
                    )
                """)

            # Создаем таблицу для хранения оценок чата
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_ratings (
                    chat_id INTEGER PRIMARY KEY,
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chat_id) REFERENCES chats (client_id) ON DELETE CASCADE
                )
            """)

            # Создаем таблицу для хранения информации о менеджерах
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS managers (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_available BOOLEAN DEFAULT TRUE,
                    active_chats INTEGER DEFAULT 0,
                    total_chats INTEGER DEFAULT 0,
                    rating REAL DEFAULT 0,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logger.info("Database tables created or already exist")
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            conn.rollback()
            raise

    def get_all_cities(self) -> list[str]:
        """Получение списка всех городов"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute("SELECT name FROM cities ORDER BY name")
            cities = [row[0] for row in cursor.fetchall()]
            logger.info(f"Retrieved {len(cities)} cities from database")
            return cities
        except sqlite3.Error as e:
            logger.error(f"Error getting cities list: {e}")
            return []
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def get_city_by_id(self, city_id: int) -> Optional[str]:
        """Получение названия города по id"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute("SELECT name FROM cities WHERE id = ?", (city_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Ошибка получения города: {e}")
            return None
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def create_chat(self, client_id: int, username: str) -> bool:
        """Создание нового чата"""
        conn, cursor = self._get_connection()
        try:
            # Проверяем, существует ли уже запись для этого пользователя
            cursor.execute("SELECT * FROM chats WHERE client_id = ?", (client_id,))
            existing_chat = cursor.fetchone()
            
            if existing_chat:
                # Если запись уже существует, обновляем только username и статус, 
                # не затрагивая другие поля
                cursor.execute(
                    "UPDATE chats SET username = ?, is_active = FALSE WHERE client_id = ?",
                    (username, client_id)
                )
            else:
                # Если записи нет, создаем новую
                cursor.execute(
                    "INSERT INTO chats (client_id, username, is_active) VALUES (?, ?, ?)",
                    (client_id, username, False)
                )
            
            conn.commit()
            logger.info(f"Chat created or updated for user {username} (ID: {client_id})")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error creating chat: {e}")
            return False
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def activate_chat(self, client_id: int, manager_id: int) -> bool:
        """Активация чата менеджером"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                "UPDATE chats SET is_active = TRUE, manager_id = ? WHERE client_id = ?",
                (manager_id, client_id)
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка активации чата: {e}")
            return False
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def close_chat(self, client_id: int) -> bool:
        """Закрытие чата"""
        conn, cursor = self._get_connection()
        try:
            # Получаем информацию о чате перед закрытием
            cursor.execute(
                "SELECT manager_id FROM chats WHERE client_id = ? AND is_active = TRUE",
                (client_id,)
            )
            chat = cursor.fetchone()

            if chat:
                # Если чат найден, закрываем его
                cursor.execute(
                    "UPDATE chats SET is_active = FALSE, manager_id = NULL WHERE client_id = ?",
                    (client_id,)
                )
                conn.commit()
                return True
            return False
        except sqlite3.Error as e:
            print(f"Ошибка закрытия чата: {e}")
            return False
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def get_active_chat(self, manager_id: int) -> Optional[tuple]:
        """Получение активного чата для менеджера"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                "SELECT * FROM chats WHERE manager_id = ? AND is_active = TRUE",
                (manager_id,)
            )
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка получения активного чата: {e}")
            return None
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def is_client_in_active_chat(self, client_id: int) -> bool:
        """Проверка, находится ли клиент в активном чате"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM chats WHERE client_id = ? AND is_active = TRUE)",
                (client_id,)
            )
            return bool(cursor.fetchone()[0])
        except sqlite3.Error as e:
            print(f"Ошибка проверки активного чата: {e}")
            return False
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def get_client_id_by_username(self, username: str) -> Optional[int]:
        """Получение client_id по username"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                "SELECT client_id FROM chats WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Ошибка получения client_id: {e}")
            return None
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def get_streets_by_city(self, city_id: int) -> List[str]:
        """Получение списка улиц по id города"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                "SELECT name FROM streets WHERE city_id = ? ORDER BY name",
                (city_id,)
            )
            streets = [row[0] for row in cursor.fetchall()]
            return streets
        except sqlite3.Error as e:
            logger.error(f"Error getting streets list: {e}")
            return []
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def get_street_by_id(self, street_id: int) -> Optional[Tuple[int, str]]:
        """Получение информации об улице по id"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                "SELECT city_id, name FROM streets WHERE id = ?",
                (street_id,)
            )
            result = cursor.fetchone()
            return result if result else None
        except sqlite3.Error as e:
            print(f"Ошибка получения улицы: {e}")
            return None
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def add_item(self, street_id: int, name: str, address: str, weekdays_time: str,
                 weekend_time: str, contact: str, geo_link: str, category: str) -> bool:
        """Добавление нового объекта"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute("""
                INSERT INTO items (street_id, name, address, weekdays_time,
                                 weekend_time, contact, geo_link, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (street_id, name, address, weekdays_time, weekend_time,
                  contact, geo_link, category))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding item: {e}")
            return False
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def get_items_by_city(self, city_id: int) -> List[Tuple]:
        """Получение списка объектов по id города"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute("""
                SELECT i.id, i.name, i.address, i.weekdays_time, i.weekend_time,
                       i.contact, i.geo_link, i.category
                FROM items i
                JOIN streets s ON i.street_id = s.id
                WHERE s.city_id = ?
                ORDER BY i.name
            """, (city_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error getting items by city: {e}")
            return []
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def get_items_by_category(self, city_id: int, category: str) -> List[Tuple]:
        """Получение списка объектов по категории в городе"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute("""
                SELECT id, name, address, weekdays_time, weekend_time,
                       contact, geo_link, category
                FROM items
                WHERE city_id = ? AND category = ?
                ORDER BY name
            """, (city_id, category))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения списка объектов по категории: {e}")
            return []
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def get_item_by_id(self, item_id: int) -> Optional[Tuple]:
        """Получение информации об объекте по id"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute("""
                SELECT city_id, name, address, weekdays_time, weekend_time,
                       contact, geo_link
                FROM items
                WHERE id = ?
            """, (item_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка получения объекта: {e}")
            return None
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def get_items_by_address(self, street: str) -> List[Tuple]:
        """Получение информации о точках по адресу"""
        conn, cursor = self._get_connection()
        try:
            # Используем LIKE для более гибкого поиска
            cursor.execute("""
                SELECT i.id, i.name, i.address, i.weekdays_time, i.weekend_time,
                       i.contact, i.geo_link, i.category
                FROM items i
                JOIN streets s ON i.street_id = s.id
                WHERE s.name LIKE ?
                ORDER BY i.name
            """, (f"%{street}%",))
            items = cursor.fetchall()
            logger.info(f"Found {len(items)} items for street: {street}")
            return items
        except sqlite3.Error as e:
            logger.error(f"Error getting items by address: {e}")
            return []
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def debug_street_info(self, street: str):
        """Отладочный метод для проверки информации об улице"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute("""
                SELECT s.id, s.name, c.name as city_name,
                       i.name as item_name, i.address
                FROM streets s
                JOIN cities c ON s.city_id = c.id
                LEFT JOIN items i ON i.street_id = s.id
                WHERE s.name LIKE ?
            """, (f"%{street}%",))
            results = cursor.fetchall()
            for row in results:
                logger.info(f"Street info: {row}")
            return results
        except sqlite3.Error as e:
            logger.error(f"Error in debug street info: {e}")
            return []
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def save_message(self, chat_id: int, sender_id: int, message_text: str, 
                    message_type: str = 'text', file_id: str = None) -> bool:
        """Сохраняет сообщение в истории чата
        
        Args:
            chat_id: ID чата (client_id)
            sender_id: ID отправителя
            message_text: Текст сообщения
            message_type: Тип сообщения ('text', 'photo', 'video', 'document', 'audio')
            file_id: ID файла в Telegram (для медиа-сообщений)
            
        Returns:
            bool: Успешность операции
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                """
                INSERT INTO messages 
                (chat_id, sender_id, message_text, message_type, file_id)
                VALUES (?, ?, ?, ?, ?)
                """, 
                (chat_id, sender_id, message_text, message_type, file_id)
            )
            conn.commit()
            logger.info(f"Message saved for chat {chat_id} from user {sender_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving message: {e}")
            conn.rollback()
            return False

    def get_chat_history(self, chat_id: int, limit: int = 50) -> list:
        """Получает историю сообщений для чата с ограничением по количеству"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                """
                SELECT id, sender_id, message_text, message_type, file_id, timestamp, is_read
                FROM messages
                WHERE chat_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (chat_id, limit)
            )
            messages = cursor.fetchall()
            # Возвращаем в порядке от старых к новым
            return list(reversed(messages))
        except sqlite3.Error as e:
            logger.error(f"Error retrieving chat history: {e}")
            return []

    def mark_messages_as_read(self, chat_id: int, user_id: int) -> bool:
        """Отмечает все сообщения к пользователю как прочитанные"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                """
                UPDATE messages
                SET is_read = TRUE
                WHERE chat_id = ? AND sender_id != ? AND is_read = FALSE
                """,
                (chat_id, user_id)
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error marking messages as read: {e}")
            conn.rollback()
            return False

    def get_unread_messages_count(self, chat_id: int, user_id: int) -> int:
        """Возвращает количество непрочитанных сообщений для пользователя"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM messages
                WHERE chat_id = ? AND sender_id != ? AND is_read = FALSE
                """,
                (chat_id, user_id)
            )
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Error counting unread messages: {e}")
            return 0

    def __del__(self):
        """Закрытие соединения при удалении объекта"""
        try:
            if hasattr(self._local, 'connection'):
                self._local.connection.close()
                delattr(self._local, 'connection')
        except Exception as e:
            logger.error(f"Error in database cleanup: {e}")

    def get_available_managers_count(self) -> int:
        """Получение количества свободных менеджеров"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute("""
                SELECT COUNT(*)
                FROM managers
                WHERE is_active = TRUE AND is_available = TRUE
            """)
            available_managers = cursor.fetchone()[0] or 0
            logger.info(f"Number of available managers: {available_managers}")
            return available_managers
        except sqlite3.Error as e:
            logger.error(f"Error getting available managers count: {e}")
            return 0
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def save_chat_rating(self, chat_id: int, rating: int, comment: str = None) -> bool:
        """Сохраняет оценку чата
        
        Args:
            chat_id: ID чата (client_id)
            rating: Оценка от 1 до 5
            comment: Комментарий к оценке (опционально)
            
        Returns:
            bool: Успешность операции
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO chat_ratings 
                (chat_id, rating, comment)
                VALUES (?, ?, ?)
                """, 
                (chat_id, rating, comment)
            )
            conn.commit()
            logger.info(f"Rating saved for chat {chat_id}: {rating}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving rating: {e}")
            conn.rollback()
            return False
            
    def get_chat_rating(self, chat_id: int) -> tuple:
        """Получает оценку чата
        
        Args:
            chat_id: ID чата (client_id)
            
        Returns:
            tuple: (rating, comment, timestamp) или None
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                """
                SELECT rating, comment, timestamp
                FROM chat_ratings
                WHERE chat_id = ?
                """,
                (chat_id,)
            )
            return cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"Error retrieving chat rating: {e}")
            return None

    def add_manager(self, manager_id: int, name: str = None, is_admin: bool = False) -> bool:
        """Добавляет нового менеджера
        
        Args:
            manager_id: ID менеджера
            name: Имя менеджера (опционально)
            is_admin: Является ли менеджер администратором
            
        Returns:
            bool: Успешность операции
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO managers 
                (id, name, is_admin, active_chats, total_chats)
                VALUES (?, ?, ?, 
                    (SELECT active_chats FROM managers WHERE id = ?), 
                    (SELECT total_chats FROM managers WHERE id = ?))
                """, 
                (manager_id, name, is_admin, manager_id, manager_id)
            )
            conn.commit()
            logger.info(f"Added manager: {manager_id} ({name})")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding manager: {e}")
            conn.rollback()
            return False
    
    def set_manager_availability(self, manager_id: int, is_available: bool) -> bool:
        """Устанавливает доступность менеджера для новых чатов
        
        Args:
            manager_id: ID менеджера
            is_available: Доступен ли менеджер для новых чатов
            
        Returns:
            bool: Успешность операции
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                """
                UPDATE managers
                SET is_available = ?, last_activity = CURRENT_TIMESTAMP
                WHERE id = ?
                """, 
                (is_available, manager_id)
            )
            conn.commit()
            logger.info(f"Manager {manager_id} availability set to {is_available}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error setting manager availability: {e}")
            conn.rollback()
            return False
    
    def update_manager_activity(self, manager_id: int) -> bool:
        """Обновляет время последней активности менеджера
        
        Args:
            manager_id: ID менеджера
            
        Returns:
            bool: Успешность операции
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                """
                UPDATE managers
                SET last_activity = CURRENT_TIMESTAMP
                WHERE id = ?
                """, 
                (manager_id,)
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating manager activity: {e}")
            conn.rollback()
            return False
    
    def get_available_manager(self) -> int:
        """Получает ID доступного менеджера с наименьшим количеством активных чатов
        
        Returns:
            int: ID менеджера или 0, если нет доступных менеджеров
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                """
                SELECT id
                FROM managers
                WHERE is_active = TRUE AND is_available = TRUE
                ORDER BY active_chats ASC, last_activity ASC
                LIMIT 1
                """
            )
            result = cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            logger.error(f"Error getting available manager: {e}")
            return 0
        finally:
            conn.close()
            delattr(self._local, 'connection')
    
    def increment_manager_active_chats(self, manager_id: int) -> bool:
        """Увеличивает счетчик активных чатов менеджера
        
        Args:
            manager_id: ID менеджера
            
        Returns:
            bool: Успешность операции
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                """
                UPDATE managers
                SET active_chats = active_chats + 1, 
                    total_chats = total_chats + 1,
                    last_activity = CURRENT_TIMESTAMP
                WHERE id = ?
                """, 
                (manager_id,)
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error incrementing manager active chats: {e}")
            conn.rollback()
            return False
    
    def decrement_manager_active_chats(self, manager_id: int) -> bool:
        """Уменьшает счетчик активных чатов менеджера
        
        Args:
            manager_id: ID менеджера
            
        Returns:
            bool: Успешность операции
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                """
                UPDATE managers
                SET active_chats = MAX(0, active_chats - 1), 
                    last_activity = CURRENT_TIMESTAMP
                WHERE id = ?
                """, 
                (manager_id,)
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error decrementing manager active chats: {e}")
            conn.rollback()
            return False
            
    def get_manager_stats(self, manager_id: int) -> tuple:
        """Получает статистику менеджера
        
        Args:
            manager_id: ID менеджера
            
        Returns:
            tuple: (active_chats, total_chats, rating) или None
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                """
                SELECT active_chats, total_chats, rating
                FROM managers
                WHERE id = ?
                """,
                (manager_id,)
            )
            return cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"Error getting manager stats: {e}")
            return None

    def get_active_chat_by_client_id(self, client_id: int) -> Optional[tuple]:
        """Получение информации о чате по ID клиента"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                "SELECT * FROM chats WHERE client_id = ? AND is_active = TRUE",
                (client_id,)
            )
            return cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"Error getting active chat by client ID: {e}")
            return None
        finally:
            conn.close()
            delattr(self._local, 'connection')

    def save_client_contact_info(self, client_id: int, name: str, phone: str, nickname: str) -> bool:
        """Сохранение контактной информации клиента"""
        conn, cursor = self._get_connection()
        try:
            # Проверяем существование полей в таблице
            cursor.execute("PRAGMA table_info(chats)")
            columns = {column[1] for column in cursor.fetchall()}
            
            # Логируем информацию о структуре таблицы для отладки
            logger.info(f"Columns in chats table: {columns}")
            
            # Проверяем наличие нужных полей в таблице
            required_fields = ['client_name', 'client_phone', 'client_nickname']
            missing_fields = [field for field in required_fields if field not in columns]
            
            if missing_fields:
                logger.error(f"Missing fields in chats table: {missing_fields}")
                # Пытаемся добавить недостающие поля
                for field in missing_fields:
                    try:
                        cursor.execute(f"ALTER TABLE chats ADD COLUMN {field} TEXT")
                        logger.info(f"Added missing field: {field}")
                    except sqlite3.Error as e:
                        logger.error(f"Error adding field {field}: {e}")
            
            # Проверяем наличие записи для этого пользователя
            cursor.execute("SELECT COUNT(*) FROM chats WHERE client_id = ?", (client_id,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Если записи нет, создаем новую
                logger.info(f"No record exists for client {client_id}, creating new one")
                cursor.execute(
                    "INSERT INTO chats (client_id, username, is_active, client_name, client_phone, client_nickname) VALUES (?, '', FALSE, ?, ?, ?)",
                    (client_id, name, phone, nickname)
                )
            else:
                # Если запись есть, обновляем ее
                logger.info(f"Updating contact info for client {client_id}")
                cursor.execute(
                    "UPDATE chats SET client_name = ?, client_phone = ?, client_nickname = ? WHERE client_id = ?",
                    (name, phone, nickname, client_id)
                )
            
            conn.commit()
            
            # Проверяем успешность обновления
            cursor.execute(
                "SELECT client_name, client_phone, client_nickname FROM chats WHERE client_id = ?",
                (client_id,)
            )
            result = cursor.fetchone()
            if result:
                logger.info(f"Contact info saved for client {client_id}: {result}")
                return True
            else:
                logger.error(f"Failed to save contact info for client {client_id} - record not found after update")
                return False
        except sqlite3.Error as e:
            logger.error(f"SQLite error saving client contact info: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving client contact info: {e}", exc_info=True)
            return False
        finally:
            try:
                conn.close()
                delattr(self._local, 'connection')
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
                # Не прерываем выполнение при ошибке закрытия соединения

    def get_client_contact_info(self, client_id: int) -> Optional[Tuple[str, str, str]]:
        """Получение контактной информации клиента"""
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                "SELECT client_name, client_phone, client_nickname FROM chats WHERE client_id = ?",
                (client_id,)
            )
            result = cursor.fetchone()
            return result if result else None
        except sqlite3.Error as e:
            logger.error(f"Error getting client contact info: {e}")
            return None
        finally:
            conn.close()
            delattr(self._local, 'connection')
