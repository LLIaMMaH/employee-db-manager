# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime


class EmployeeDB:
    def __init__(self, db_name='employees.db'):
        self.db_name = db_name
        self.conn = None

    def _connect(self):
        """Устанавливает соединение с БД"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка подключения к базе: {str(e)}")

    def _close(self):
        """Закрывает соединение с БД"""
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error:
                pass
            finally:
                self.conn = None

    def _ensure_table_exists(self):
        """Гарантирует что таблица существует"""
        try:
            self._connect()
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
            if not cursor.fetchone():
                self.create_table()
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка проверки таблицы: {str(e)}")
        finally:
            self._close()

    def create_table(self):
        """Создает таблицу сотрудников"""
        try:
            self._connect()
            cursor = self.conn.cursor()
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS employees
                           (
                               id         INTEGER PRIMARY KEY AUTOINCREMENT,
                               full_name  TEXT NOT NULL,
                               birth_date TEXT NOT NULL,
                               gender     TEXT NOT NULL
                           )
                           """)
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка создания таблицы: {str(e)}")
        finally:
            self._close()

    def add_employee(self, full_name, birth_date, gender):
        """Добавляет нового сотрудника"""
        try:
            # Проверка формата даты
            datetime.strptime(birth_date, '%Y-%m-%d')

            # Нормализация данных
            gender = 'Male' if gender.lower() in ('м', 'm', 'male', '1') else 'Female'

            self._ensure_table_exists()
            self._connect()
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO employees (full_name, birth_date, gender) VALUES (?, ?, ?)",
                (full_name, birth_date, gender)
            )
            self.conn.commit()
            return True
        except ValueError:
            print("Ошибка: Неверный формат даты. Используйте YYYY-MM-DD")
            return False
        except Exception as e:
            print(f"Ошибка при добавлении сотрудника: {e}")
            return False
        finally:
            self._close()

    def get_all_employees(self):
        """Возвращает всех сотрудников"""
        try:
            self._ensure_table_exists()
            self._connect()
            cursor = self.conn.cursor()
            cursor.execute("""
                           SELECT full_name,
                                  birth_date,
                                  gender,
                                  (strftime('%Y', 'now') - strftime('%Y', birth_date)) -
                                  (strftime('%m-%d', 'now') < strftime('%m-%d', birth_date)) as age
                           FROM employees
                           GROUP BY full_name, birth_date
                           ORDER BY full_name
                           """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка получения сотрудников: {str(e)}")
        finally:
            self._close()

    def generate_test_data(self, count=1000000, special=100):
        """Генерирует тестовые данные"""
        from random import choice, randint
        from datetime import date, timedelta

        try:
            self._ensure_table_exists()
            self._connect()
            cursor = self.conn.cursor()

            # Основные данные
            for i in range(count):
                gender = choice(['Male', 'Female'])
                first_name = f"Name{randint(1, 1000)}"
                last_name = f"Lastname{randint(1, 1000)}"
                birth_date = date.today() - timedelta(days=randint(18 * 365, 65 * 365))

                cursor.execute(
                    "INSERT INTO employees (full_name, birth_date, gender) VALUES (?, ?, ?)",
                    (f"{last_name} {first_name}", birth_date.isoformat(), gender)
                )

            # Специальные записи
            for i in range(special):
                birth_date = date.today() - timedelta(days=randint(18 * 365, 65 * 365))
                cursor.execute(
                    "INSERT INTO employees (full_name, birth_date, gender) VALUES (?, ?, ?)",
                    (f"Fake_{i} Surname", birth_date.isoformat(), 'Male')
                )

            self.conn.commit()
            return count + special
        finally:
            self._close()

    def query_male_f(self):
        """Запрос мужчин с фамилией на F"""
        try:
            self._ensure_table_exists()
            self._connect()
            cursor = self.conn.cursor()
            cursor.execute("""
                           SELECT full_name,
                                  birth_date,
                                  gender,
                                  (strftime('%Y', 'now') - strftime('%Y', birth_date)) -
                                  (strftime('%m-%d', 'now') < strftime('%m-%d', birth_date)) as age
                           FROM employees
                           WHERE gender = 'Male'
                             AND full_name LIKE 'F%'
                           """)
            return cursor.fetchall()
        finally:
            self._close()

    def optimize_database(self):
        """Создает индексы для ускорения запросов"""
        try:
            self._connect()
            cursor = self.conn.cursor()

            # Создаем составной индекс для часто используемого запроса
            cursor.execute("""
                           CREATE INDEX IF NOT EXISTS idx_gender_lastname
                               ON employees(gender, substr(full_name, 1, 1))
                           """)

            # Оптимизация для поиска по полу
            cursor.execute("""
                           CREATE INDEX IF NOT EXISTS idx_gender
                               ON employees(gender)
                           """)

            # Оптимизация для поиска по первой букве фамилии
            cursor.execute("""
                           CREATE INDEX IF NOT EXISTS idx_first_letter
                               ON employees(substr(full_name, 1, 1))
                           """)

            self.conn.commit()
            return True
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка оптимизации БД: {str(e)}")
        finally:
            self._close()
