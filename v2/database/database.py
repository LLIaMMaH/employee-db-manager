# -*- coding: utf-8 -*-

import sqlite3
import psycopg2
from typing import List, Dict, Tuple, Optional, Union
from datetime import date, datetime
import time
from core.logging import get_module_logger


class Database:
    """Унифицированный интерфейс для работы с SQLite и PostgreSQL"""

    def __init__(self, db_type: str = 'sqlite', db_name: str = 'employees.db'):
        """
        Инициализация подключения к БД

        :param db_type: Тип БД ('sqlite' или 'postgresql')
        :param db_name: Имя базы данных
        """
        self.logger = get_module_logger(__name__)
        self.db_type = db_type
        self.db_name = db_name
        self.conn = None

    def connect(self) -> None:
        """Устанавливает соединение с базой данных"""
        try:
            if self.db_type == 'sqlite':
                self.conn = sqlite3.connect(self.db_name)
                # Включение поддержки внешних ключей для SQLite
                self.conn.execute("PRAGMA foreign_keys = ON")
            elif self.db_type == 'postgresql':
                self.conn = psycopg2.connect(
                    host="localhost",
                    database=self.db_name,
                    user="postgres",
                    password="postgres",
                    connect_timeout=10
                )
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")

    def close(self) -> None:
        """Закрывает соединение с базой данных"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def _execute(self, query: str, params: Tuple = None, fetch: bool = False) -> Optional[List[Tuple]]:
        """
        Универсальный метод выполнения SQL-запросов

        :param query: SQL-запрос
        :param params: Параметры запроса
        :param fetch: Нужно ли возвращать результат
        :return: Результат запроса или None
        """
        cursor = None
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(query, params or ())

            if fetch:
                result = cursor.fetchall()
                self.conn.commit()
                return result
            else:
                self.conn.commit()
                return None

        except Exception as e:
            if self.conn:
                self.conn.rollback()
            raise RuntimeError(f"Database error: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            self.close()

    def create_table(self) -> None:
        """Создает таблицу employees, если она не существует"""
        if self.db_type == 'sqlite':
            query = """
                    CREATE TABLE IF NOT EXISTS employees
                    (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT NOT NULL,
                        birth_date DATE NOT NULL,
                        gender TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
        else:  # postgresql
            query = """
                    CREATE TABLE IF NOT EXISTS employees
                    (
                        id SERIAL PRIMARY KEY,
                        full_name VARCHAR(50) NOT NULL,
                        birth_date DATE NOT NULL,
                        gender VARCHAR(10) NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW
                    (
                    )
                        )
                    """
        self._execute(query)

    def insert_employee(self, full_name: str, birth_date: Union[date, str], gender: str) -> int:
        """
        Добавляет нового сотрудника в базу данных

        :param full_name: Полное имя сотрудника
        :param birth_date: Дата рождения (объект date или строка в формате YYYY-MM-DD)
        :param gender: Пол ('Male' или 'Female')
        :return: ID добавленной записи
        """
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()

        if self.db_type == 'sqlite':
            query = """
                    INSERT INTO employees (full_name, birth_date, gender)
                    VALUES (?, ?, ?) RETURNING id
                    """
        else:
            query = """
                    INSERT INTO employees (full_name, birth_date, gender)
                    VALUES (%s, %s, %s) RETURNING id
                    """

        result = self._execute(
            query,
            (full_name, birth_date.isoformat(), gender),
            fetch=True
        )
        return result[0][0] if result else None

    def batch_insert_employees(self, employees: List[Dict[str, Union[str, date]]]) -> int:
        """
        Массовое добавление сотрудников

        :param employees: Список словарей с данными сотрудников
        :return: Количество добавленных записей
        """
        if not employees:
            return 0

        # Подготовка данных
        data = [
            (
                emp['full_name'],
                emp['birth_date'].isoformat() if isinstance(emp['birth_date'], date) else emp['birth_date'],
                emp['gender']
            )
            for emp in employees
        ]

        if self.db_type == 'sqlite':
            query = """
                    INSERT INTO employees (full_name, birth_date, gender)
                    VALUES (?, ?, ?)
                    """
        else:
            query = """
                    INSERT INTO employees (full_name, birth_date, gender)
                    VALUES (%s, %s, %s)
                    """

        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.executemany(query, data)
            self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Batch insert failed: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            self.close()

    def get_all_employees(self) -> List[Dict[str, Union[str, date, int]]]:
        """
        Получает список всех сотрудников

        :return: Список словарей с информацией о сотрудниках
        """
        query = """
                SELECT id, full_name, birth_date, gender, created_at
                FROM employees
                ORDER BY full_name
                """
        result = self._execute(query, fetch=True)

        employees = []
        for row in result:
            employees.append({
                'id': row[0],
                'full_name': row[1],
                'birth_date': datetime.strptime(row[2], '%Y-%m-%d').date() if isinstance(row[2], str) else row[2],
                'gender': row[3],
                'created_at': row[4]
            })
        return employees

    def get_employees_by_gender_and_name_start(self, gender: str, name_start: str) -> Tuple[List[Dict], float]:
        """
        Получает сотрудников по полу и первой букве фамилии с замером времени

        :param gender: Пол для фильтрации
        :param name_start: Первая буква фамилии
        :return: (Список сотрудников, время выполнения в секундах)
        """
        start_time = time.time()

        query = """
                SELECT id, full_name, birth_date, gender
                FROM employees
                WHERE gender = ?
                  AND full_name LIKE ?
                """ if self.db_type == 'sqlite' else """
                                                     SELECT id, full_name, birth_date, gender
                                                     FROM employees
                                                     WHERE gender = %s
                                                       AND full_name LIKE %s
                                                     """

        params = (gender, f"{name_start}%")
        try:
            result = self._execute(query, params, fetch=True)

            employees = []
            for row in result:
                employees.append({
                    'id': row[0],
                    'full_name': row[1],
                    'birth_date': datetime.strptime(row[2], '%Y-%m-%d').date() if isinstance(row[2], str) else row[2],
                    'gender': row[3]
                })

            execution_time = time.time() - start_time
            self.logger.info(
                f"Query returned {len(employees)} employees in {execution_time:.4f} seconds"
            )
            return employees, execution_time

        except Exception as e:
            self.logger.error(f"Query failed: {str(e)}")
            raise RuntimeError("Failed to execute query") from e

    def create_indexes(self):
        """Создает оптимизированные индексы"""
        self.connect()
        try:
            cursor = self.conn.cursor()
            # TODO: Проверку, нужно ли создавать данные индексы

            # Основной составной индекс для нашего запроса
            cursor.execute("""
                           CREATE INDEX IF NOT EXISTS idx_gender_fname
                               ON employees(gender, substr(full_name, 1, 1))
                           """)

            # Дополнительные индексы для других возможных запросов
            cursor.execute("""
                           CREATE INDEX IF NOT EXISTS idx_full_name
                               ON employees(full_name)
                           """)

            cursor.execute("""
                           CREATE INDEX IF NOT EXISTS idx_birth_date
                               ON employees(birth_date)
                           """)

            self.conn.commit()
        finally:
            self.close()

    def table_exists(self) -> bool:
        """Проверяет, существует ли таблица employees"""
        if self.db_type == 'sqlite':
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name='employees'"
        else:
            query = """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_name = 'employees'
                    """

        result = self._execute(query, fetch=True)
        return bool(result)
