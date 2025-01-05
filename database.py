import sqlite3
from typing import Optional


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
            # Удаляем таблицу если она существует, чтобы пересоздать
            self.cursor.execute("DROP TABLE IF EXISTS chats")

            # Создаем таблицу заново
            self.cursor.execute("""
                CREATE TABLE chats (
                    client_id INTEGER PRIMARY KEY,
                    manager_id INTEGER,
                    is_active BOOLEAN DEFAULT FALSE,
                    username TEXT
                )
            """)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Ошибка создания таблицы: {e}")
            raise

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

    def __del__(self):
        """Закрытие соединения при удалении объекта"""
        if self.connection:
            self.connection.close()
