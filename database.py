import sqlite3
from typing import Optional, List, Tuple


class Database:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.connection = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Создание подключения к базе данных"""
        try:
            self.connection = sqlite3.connect(self.db_file)
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise

    def _create_tables(self):
        """Создание необходимых таблиц"""
        try:
            # Удаляем таблицы если они существуют
            self.cursor.execute("DROP TABLE IF EXISTS chats")
            self.cursor.execute("DROP TABLE IF EXISTS cities")
            self.cursor.execute("DROP TABLE IF EXISTS streets")
            self.cursor.execute("DROP TABLE IF EXISTS items")

            # Создаем таблицы заново
            self.cursor.execute("""
                CREATE TABLE chats (
                    client_id INTEGER PRIMARY KEY,
                    manager_id INTEGER,
                    is_active BOOLEAN DEFAULT FALSE,
                    username TEXT
                )
            """)

            self.cursor.execute("""
                CREATE TABLE cities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """)

            self.cursor.execute("""
                CREATE TABLE streets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    FOREIGN KEY (city_id) REFERENCES cities (id) ON DELETE CASCADE
                )
            """)

            self.cursor.execute("""
                CREATE TABLE items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    weekdays_time TEXT,
                    weekend_time TEXT,
                    contact TEXT,
                    geo_link TEXT,
                    category TEXT,
                    FOREIGN KEY (city_id) REFERENCES cities (id) ON DELETE CASCADE
                )
            """)

            # Заполняем таблицу городов
            cities = [
                "Алматы", "Актобе", "Астана", "Атырау", "Караганда",
                "Кокшетау", "Кызылорда", "Павлодар", "Петропавловск",
                "Семей", "Степногорск", "Темиртау", "Туркестан",
                "Уральск", "Усть-Каменогорск", "Шымкент", "Экибастуз"
            ]
            
            self.cursor.executemany(
                "INSERT INTO cities (name) VALUES (?)",
                [(city,) for city in cities]
            )

            # Список улиц с привязкой к городам
            streets_data = [
                # Актобе
                (2, "Проспект 312 Стрелковой Дивизии 3/2"),
                # Алматы
                (1, "проспект Рыскулова 103"),
                (1, "улица Жандосова 2Б"),
                (1, "микрорайон Аксай 1А 16Б"),
                (1, "улица Васнецова 4/93"),
                (1, "проспект Суюнбая 284"),
                (1, "улица Бережинского 7"),
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
                # Семей
                (9, "улица Парковая 57Б"),
                # Петропавловск
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

            self.cursor.executemany(
                "INSERT INTO streets (city_id, name) VALUES (?, ?)",
                streets_data
            )

            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Ошибка создания таблиц: {e}")
            raise

    def get_all_cities(self) -> list[str]:
        """Получение списка всех городов"""
        try:
            self.cursor.execute("SELECT name FROM cities ORDER BY name")
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Ошибка получения списка городов: {e}")
            return []

    def get_city_by_id(self, city_id: int) -> Optional[str]:
        """Получение названия города по id"""
        try:
            self.cursor.execute("SELECT name FROM cities WHERE id = ?", (city_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Ошибка получения города: {e}")
            return None

    def create_chat(self, client_id: int, username: str) -> bool:
        """Создание нового чата"""
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO chats (client_id, username, is_active) VALUES (?, ?, ?)",
                (client_id, username, False)
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка создания чата: {e}")
            return False

    def activate_chat(self, client_id: int, manager_id: int) -> bool:
        """Активация чата менеджером"""
        try:
            self.cursor.execute(
                "UPDATE chats SET is_active = TRUE, manager_id = ? WHERE client_id = ?",
                (manager_id, client_id)
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка активации чата: {e}")
            return False

    def close_chat(self, client_id: int) -> bool:
        """Закрытие чата"""
        try:
            # Получаем информацию о чате перед закрытием
            self.cursor.execute(
                "SELECT manager_id FROM chats WHERE client_id = ? AND is_active = TRUE",
                (client_id,)
            )
            chat = self.cursor.fetchone()

            if chat:
                # Если чат найден, закрываем его
                self.cursor.execute(
                    "UPDATE chats SET is_active = FALSE, manager_id = NULL WHERE client_id = ?",
                    (client_id,)
                )
                self.connection.commit()
                return True
            return False
        except sqlite3.Error as e:
            print(f"Ошибка закрытия чата: {e}")
            return False

    def get_active_chat(self, manager_id: int) -> Optional[tuple]:
        """Получение активного чата для менеджера"""
        try:
            self.cursor.execute(
                "SELECT * FROM chats WHERE manager_id = ? AND is_active = TRUE",
                (manager_id,)
            )
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка получения активного чата: {e}")
            return None

    def is_client_in_active_chat(self, client_id: int) -> bool:
        """Проверка, находится ли клиент в активном чате"""
        try:
            self.cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM chats WHERE client_id = ? AND is_active = TRUE)",
                (client_id,)
            )
            return bool(self.cursor.fetchone()[0])
        except sqlite3.Error as e:
            print(f"Ошибка проверки активного чата: {e}")
            return False

    def get_client_id_by_username(self, username: str) -> Optional[int]:
        """Получение client_id по username"""
        try:
            self.cursor.execute(
                "SELECT client_id FROM chats WHERE username = ?",
                (username,)
            )
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Ошибка получения client_id: {e}")
            return None

    def get_streets_by_city(self, city_id: int) -> List[str]:
        """Получение списка улиц по id города"""
        try:
            self.cursor.execute(
                "SELECT name FROM streets WHERE city_id = ? ORDER BY name",
                (city_id,)
            )
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Ошибка получения списка улиц: {e}")
            return []

    def get_street_by_id(self, street_id: int) -> Optional[Tuple[int, str]]:
        """Получение информации об улице по id"""
        try:
            self.cursor.execute(
                "SELECT city_id, name FROM streets WHERE id = ?",
                (street_id,)
            )
            result = self.cursor.fetchone()
            return result if result else None
        except sqlite3.Error as e:
            print(f"Ошибка получения улицы: {e}")
            return None

    def add_item(self, city_id: int, name: str, address: str, weekdays_time: str, 
                 weekend_time: str, contact: str, geo_link: str, category: str) -> bool:
        """Добавление нового объекта"""
        try:
            self.cursor.execute("""
                INSERT INTO items (city_id, name, address, weekdays_time, 
                                 weekend_time, contact, geo_link, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (city_id, name, address, weekdays_time, weekend_time, 
                  contact, geo_link, category))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка добавления объекта: {e}")
            return False

    def get_items_by_city(self, city_id: int) -> List[Tuple]:
        """Получение списка объектов по id города"""
        try:
            self.cursor.execute("""
                SELECT id, name, address, weekdays_time, weekend_time, 
                       contact, geo_link, category 
                FROM items 
                WHERE city_id = ?
                ORDER BY name
            """, (city_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения списка объектов: {e}")
            return []

    def get_items_by_category(self, city_id: int, category: str) -> List[Tuple]:
        """Получение списка объектов по категории в городе"""
        try:
            self.cursor.execute("""
                SELECT id, name, address, weekdays_time, weekend_time,
                       contact, geo_link, category
                FROM items
                WHERE city_id = ? AND category = ?
                ORDER BY name
            """, (city_id, category))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения списка объектов по категории: {e}")
            return []

    def get_item_by_id(self, item_id: int) -> Optional[Tuple]:
        """Получение информации об объекте по id"""
        try:
            self.cursor.execute("""
                SELECT city_id, name, address, weekdays_time, weekend_time,
                       contact, geo_link
                FROM items
                WHERE id = ?
            """, (item_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка получения объекта: {e}")
            return None

    def __del__(self):
        """Закрытие соединения при удалении объекта"""
        if self.connection:
            self.connection.close()
