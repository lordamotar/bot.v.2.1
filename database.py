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
        """Создание необходимых таблиц"""
        conn, cursor = self._get_connection()
        try:
            # Удаляем таблицы если они существуют
            cursor.execute("DROP TABLE IF EXISTS chats")
            cursor.execute("DROP TABLE IF EXISTS cities")
            cursor.execute("DROP TABLE IF EXISTS streets")
            cursor.execute("DROP TABLE IF EXISTS items")

            # Создаем таблицы заново
            cursor.execute("""
                CREATE TABLE chats (
                    client_id INTEGER PRIMARY KEY,
                    manager_id INTEGER,
                    is_active BOOLEAN DEFAULT FALSE,
                    username TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE cities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """)

            cursor.execute("""
                CREATE TABLE streets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    FOREIGN KEY (city_id) REFERENCES cities (id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE items (
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
                (street_id, street_city_mapping[street_id], address, weekdays, weekend, contact, geo, "Магазин")
                for street_id, address, weekdays, weekend, contact, geo in [
                    # Актобе
                    (streets_mapping["Проспект 312 Стрелковой Дивизии 3/2"],
                     "Проспект 312 Стрелковой Дивизии 3/2",
                     "Пн-Пт: 09:00-18:00", "Сб: 09:00-14:00",
                     "7(705)752-33-07, 7(771)350-34-83", "https://go.2gis.com/zjq6q"),

                    # Алматы
                    (streets_mapping["проспект Рыскулова 103"],
                     "проспект Рыскулова 103",
                     "09:00-20:00", "Без выходных",
                     "7(705) 752-06-45", "https://go.2gis.com/9urut"),
                    (streets_mapping["улица Жандосова 2Б"],
                     "улица Жандосова 2Б",
                     "09:00-20:00", "Без выходных",
                     "7(771) 350-34-72", "https://go.2gis.com/4n01z"),
                    (streets_mapping["микрорайон Аксай 1А 16Б"],
                     "микрорайон Аксай 1А 16Б",
                     "09:00-20:00", "Без выходных",
                     "7(705) 795-59-61", "https://go.2gis.com/vevjl"),
                    (streets_mapping["улица Васнецова 4/93"],
                     "улица Васнецова 4/93",
                     "09:00-20:00", "Без выходных",
                     "7(705) 798-34-17", "https://go.2gis.com/5bb53"),
                    (streets_mapping["проспект Суюнбая 284"],
                     "проспект Суюнбая 284",
                     "Пн-Пт: 09:00-18:00 (Обед: 13:00-14:00)", "Сб 09:00-14:00 Вс: Выходной",
                     "8(7272)90-28-22", "https://go.2gis.com/ilsyk"),
                    (streets_mapping["улица Бережинского 7"],
                     "улица Бережинского 7",
                     "Пн-Пт: 09:00-18:00", "Сб: 09:00-14:00 Вс: Выходной",
                     "7(705) 735-46-30", "https://go.2gis.com/klhyg"),

                    # Астана
                    (streets_mapping["улица Айнакол 111"],
                     "улица Айнакол 111",
                     "Пн-Пт: 09:00-20:00", "Сб-Вс: 09:00-16:00",
                     "7(705)795-74-87, 7(771)051-71-61", "https://go.2gis.com/bfw9sk"),
                    (streets_mapping["улица Сакен Сейфуллин 11/1в"],
                     "улица Сакен Сейфуллин 11/1в",
                     "Пн-Пт: 09:00-20:00", "Сб-Вс: 09:00-16:00",
                     "7(705)795--87-08, 7(771)840-31-02", "https://go.2gis.com/nghvh"),
                    (streets_mapping["шоссе Алаш 42"],
                     "шоссе Алаш 42",
                     "Пн-Пт: 09:00-20:00", "Сб-Вс: 09:00-16:00",
                     "7(771) 350-34-45", "https://go.2gis.com/1uaff"),

                    # Атырау
                    (streets_mapping["Северная промышленная зона 45"],
                     "Северная промышленная зона 45",
                     "Пн-Сб: 09:00-18:00 (13:00-14:00 обед)", "Вс: Выходной",
                     "7(777) 075-86-57", "https://go.2gis.com/v33tb"),

                    # Караганда
                    (streets_mapping["134-й учетный квартал к2"],
                     "134-й учетный квартал к2",
                     "Пн-Пт: 09:00-18:00", "Сб-Вс: 09:00-16:00",
                     "7(705) 752-33-40", "https://go.2gis.com/soas1"),
                    (streets_mapping["улица Бытовая 17/1"],
                     "улица Бытовая 17/1",
                     "Пн-Пт: 09:00-18:00", "Сб-Вс: 09:00-16:00",
                     "7(705) 752-37-14", "https://go.2gis.com/zo9tq"),

                    # Кокшетау
                    (streets_mapping["улица Шокана Уалиханова 197"],
                     "улица Шокана Уалиханова 197",
                     "Пн-Пт: 09:00-20:00", "Сб-Вс: 09:00-16:00",
                     "7(705) 795-19-25", "https://go.2gis.com/rzaj6"),

                    # Кызылорда
                    (streets_mapping["ул. Коркыт ата 125"],
                     "ул. Коркыт ата 125",
                     "Пн-Пт: 09:00-18:00", "Сб-Вс: 09:00-17:00",
                     "7(771) 350-34-06", "https://go.2gis.com/ykxrr"),
                    (streets_mapping["улица Узакбая Караманова 103а"],
                     "улица Узакбая Караманова 103а (бывш. ул.Шымбая)",
                     "Пн-Пт: 09:00-19:00", "Сб-Вс: 09:00-18:00",
                     "7(771) 840-30-64", "https://go.2gis.com/a34xgj"),

                    # Павлодар
                    (streets_mapping["Северная промышленная зона 190/1"],
                     "Северная промышленная зона 190/1",
                     "Пн-Сб: 09:00-17:00 (13:00-14:00 обед)", "Вс: Выходной",
                     "7(771) 051-22-45", "https://go.2gis.com/71ouz"),
                    (streets_mapping["улица Транспортная 17/9"],
                     "улица Транспортная 17/9",
                     "Пн-Пт: 09:00-19:00", "Сб-Вс: 09:00-17:00",
                     "7(705) 752-28-11", "https://go.2gis.com/y42or"),
                    (streets_mapping["улица Луначарского 44/2"],
                     "улица Луначарского 44/2",
                     "Пн-Пт: 09:00-19:00", "Сб-Вс: 09:00-17:00",
                     "7(771) 350-34-38", "https://go.2gis.com/wd4ph"),

                    # Петропавловск
                    (streets_mapping["улица Парковая 57Б"],
                     "улица Парковая 57Б",
                     "Пн-Пт: 09:00-19:00", "Сб-Вс: 09:00-16:00",
                     "7(771) 051-22-24", "https://go.2gis.com/c72rq"),

                    # Семей
                    (streets_mapping["трасса Семей-Павлодар 10"],
                     "трасса Семей-Павлодар 10",
                     "Пн-Сб: 08:00-17:00 (12:00-13:00 обед)", "Вс: Выходной",
                     "7(705) 795-28-38", "https://go.2gis.com/cewyn"),
                    (streets_mapping["улица Кутжанова 23"],
                     "улица Кутжанова 23",
                     "Пн-Пт: 08:00-18:00", "Сб-Вс: 09:00-16:00",
                     "7(771) 350-34-36", "https://go.2gis.com/u8qq1"),
                    (streets_mapping["улица Бозтаева 106"],
                     "улица Бозтаева 106",
                     "Пн-Пт: 08:00-18:00", "Сб-Вс: 09:00-16:00",
                     "7(771) 350-30-02", "https://go.2gis.com/py62o"),
                    (streets_mapping["улица Красный Пильщик 36/2"],
                     "улица Красный Пильщик 36/2",
                     "Пн-Пт: 09:00-18:00", "Сб: 09:00-14:00 Вс: Выходной",
                     "7(771) 840-32-59", "https://go.2gis.com/brhzz"),

                    # Степногорск
                    (streets_mapping["2-й микрорайон 77"],
                     "2-й микрорайон 77",
                     "Пн-Пт: 09:00-20:00", "Сб-Вс: 09:00-16:00",
                     "7(705) 795-77-81", "https://go.2gis.com/rzaj6"),

                    # Темиртау
                    (streets_mapping["улица Мичурина 36"],
                     "улица Мичурина 36",
                     "Пн-Сб: 09:00-18:00", "Сб: 09:00-16:00 Вс: 10:00-16:00",
                     "7(771) 051-70-32", "https://go.2gis.com/x6ruv"),
                    # Туркестан
                    (streets_mapping["улица Кудайбердинова 108А"],
                     "улица Кудайбердинова 108А",
                     "Пн-Пт: 09:00-19:00", "Сб-Вс: 09:00-16:00",
                     "7(771) 051-15-47", "https://go.2gis.com/8gf4l"),

                    # Уральск
                    (streets_mapping["микрорайон Северо-Восток 2 23/2"],
                     "микрорайон Северо-Восток 2 23/2",
                     "Пн-Вс: 09:00-18:00", "",
                     "7(777) 075-85-43", "https://go.2gis.com/sgzhzo"),
                    (streets_mapping["улица Поповича 12А"],
                     "улица Поповича 12А",
                     "Пн-Пт: 09:00-18:00 (13.00-14.00 обед)", "Сб: 09:00-13:00 Вс: выходной",
                     "7(705) 795-70-33", "https://go.2gis.com/6scux"),

                    # Усть-Каменогорск
                    (streets_mapping["ул. Жибек Жолы 19"],
                     "ул. Жибек Жолы 19",
                     "Пт-Вс: 09:00 - 19:00", "",
                     "7(771) 051-90-88", "https://go.2gis.com/20rzj"),
                    (streets_mapping["проспект Абая 160"],
                     "проспект Абая 160",
                     "Пт-Вс: 09:00-19:00", "Без выходных",
                     "7(771) 305-47-85", "https://go.2gis.com/f6jpg"),
                    (streets_mapping["улица Тракторная 24"],
                     "улица Тракторная 24",
                     "Пн-Пт: 09:00-18:00 (13:00-14:00 обед)", "Сб: 09:00-14:00 Вс: Выходной",
                     "7(771) 302-54-73", "https://go.2gis.com/whyw0"),
                    (streets_mapping["проспект Абая 154/1"],
                     "проспект Абая 154/1",
                     "Пт-Вс: 09:00-18:00", "Без выходных",
                     "7(771) 302-54-74", "https://go.2gis.com/1un5ec"),

                    # Шымкент
                    (streets_mapping["ул. Аргынбекова 3"],
                     "ул. Аргынбекова 3",
                     "Пн-Пт: 09:00-19:00", "Сб: 09:00-16:00 Вс: Выходной",
                     "7(771) 840-29-72", "https://go.2gis.com/jcspt"),
                    (streets_mapping["226-й квартал ст353"],
                     "226-й квартал ст353 (склад Арай)",
                     "Пн-Пт: 09:00-18:00", "Сб: 09:00-14:00 Вс: Выходной",
                     "7(705) 752-06-44", "https://go.2gis.com/yasax"),
                    (streets_mapping["Тамерлановское шоссе 128/7"],
                     "Тамерлановское шоссе 128/7",
                     "Пн-Пт: 09:00-19:00", "Сб-Вс: 09:00-16:00",
                     "7(771) 840-29-55", "https://go.2gis.com/y6e42"),
                    (streets_mapping["улица Жибек жолы 886"],
                     "улица Жибек жолы 886",
                     "Пн-Пт: 09:00-19:00", "Сб-Вс: 09:00-16:00",
                     "7(771) 202-96-94", "https://go.2gis.com/grbzy"),
                    (streets_mapping["улица Пищевикова 6"],
                     "улица Пищевикова 6",
                     "Пн-Пт: 09:00-18:00", "Сб: 09:00-14:00 Вс: Выходной",
                     "7(771) 350-34-88", "https://go.2gis.com/0hwbm"),

                    # Экибастуз
                    (streets_mapping["улица Желтоксан 9"],
                     "улица Желтоксан 9",
                     "Пн-Пт: 09:00-18:00", "Сб: 09:00-16:00 Вс: Выходной",
                     "7(705) 795-87-95", "https://go.2gis.com/t0me1")
                ]
            ]

            cursor.executemany("""
                INSERT INTO items (street_id, name, address, weekdays_time,
                                  weekend_time, contact, geo_link, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, items_data)

            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            raise
        finally:
            conn.close()
            delattr(self._local, 'connection')

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
            cursor.execute(
                "INSERT OR REPLACE INTO chats (client_id, username, is_active) VALUES (?, ?, ?)",
                (client_id, username, False)
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка создания чата: {e}")
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
            logger.info(f"Retrieved {len(streets)} streets for city_id: {city_id}")
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

    def __del__(self):
        """Закрытие соединения при удалении объекта"""
        try:
            if hasattr(self._local, 'connection'):
                self._local.connection.close()
                delattr(self._local, 'connection')
        except Exception as e:
            logger.error(f"Error in database cleanup: {e}")
