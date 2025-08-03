# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Union

from core.config import settings
from core.logging import get_module_logger
from database.database import Database
from database.models import Employee


class EmployeeManager:
    """Основной класс для бизнес-логики работы с сотрудниками"""

    def __init__(self, db_type: str = None):
        """
        Инициализация менеджера

        :param db_type: Тип БД (если None, берется из настроек)
        """
        self.logger = get_module_logger(__name__)
        self.db = Database(
            db_type=db_type or settings.DB_TYPE,
            db_name=settings.DB_NAME
        )
        self.logger.info(f"EmployeeManager initialized with DB type: {str(self.db.db_type)}")

    def table_exists(self) -> bool:
        """
        Проверяет существование таблицы employees

        :return: True если таблица существует, иначе False
        """
        try:
            exists = self.db.table_exists()
            self.logger.debug(f"Table exists check: {exists}")
            return exists
        except Exception as e:
            self.logger.error(f"Failed to check table existence: {str(e)}")
            raise RuntimeError("Failed to check table existence") from e

    def ensure_table_exists(self) -> None:
        """
        Гарантирует что таблица существует.
        Создает если не существует.

        :raises RuntimeError: Если не удалось создать таблицу
        """
        if not self.table_exists():
            self.logger.info("Creating employees table")
            try:
                self.db.create_table()
                if not self.table_exists():
                    raise RuntimeError("Table creation failed")
            except Exception as e:
                self.logger.critical(f"Failed to initialize database: {str(e)}")
                raise RuntimeError("Failed to initialize database") from e

    def add_employee(self, full_name: str, birth_date: Union[date, str], gender_input: str) -> Employee:
        """
        Добавляет нового сотрудника с валидацией данных

        :param full_name: Полное имя сотрудника
        :param birth_date: Дата рождения (date или строка YYYY-MM-DD)
        :param gender_input: Пол (любой валидный вариант)
        :return: Объект Employee
        :raises ValueError: При невалидных данных
        """
        self.ensure_table_exists()

        try:
            # Преобразование даты
            if isinstance(birth_date, str):
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()

            # Создание объекта сотрудника (валидация происходит в модели)
            employee = Employee(
                full_name=full_name,
                birth_date=birth_date,
                gender=gender_input
            )

            # Сохранение в БД
            employee_id = self.db.insert_employee(
                full_name=employee.full_name,
                birth_date=employee.birth_date,
                gender=employee.gender
            )

            self.logger.info(f"Added new employee with ID: {employee_id}")
            return employee

        except ValueError as ve:
            self.logger.warning(f"Validation error for employee data: {str(ve)}")
            raise ValueError(f"Invalid employee data: {str(ve)}") from ve
        except Exception as e:
            self.logger.error(f"Failed to add employee: {str(e)}")
            raise RuntimeError("Failed to add employee to database") from e

    def batch_add_employees(self, employees_data: List[Dict[str, Union[str, date]]]) -> int:
        """
        Массовое добавление сотрудников

        :param employees_data: Список словарей с данными сотрудников
        :return: Количество успешно добавленных сотрудников
        :raises RuntimeError: При ошибках базы данных
        """
        self.ensure_table_exists()
        self.logger.info(f"Starting batch add of {len(employees_data)} employees")

        valid_employees = []
        error_count = 0

        # Валидация и подготовка данных
        for emp_data in employees_data:
            try:
                emp = Employee(
                    full_name=emp_data['full_name'],
                    birth_date=emp_data['birth_date'],
                    gender=emp_data['gender']
                )
                valid_employees.append({
                    'full_name': emp.full_name,
                    'birth_date': emp.birth_date,
                    'gender': emp.gender
                })
            except (KeyError, ValueError) as e:
                error_count += 1
                self.logger.warning(f"Invalid employee data in batch: {str(e)}")

        # Пакетная вставка
        try:
            added_count = self.db.batch_insert_employees(valid_employees)
            self.logger.info(
                f"Batch insert completed. Success: {added_count}, Errors: {error_count}"
            )
            return added_count
        except Exception as e:
            self.logger.error(f"Batch insert failed: {str(e)}")
            raise RuntimeError("Failed to perform batch insert") from e

    def get_all_employees(self) -> List[Employee]:
        """
        Получает список всех сотрудников

        :return: Список объектов Employee
        :raises RuntimeError: При ошибках базы данных
        """
        self.ensure_table_exists()
        self.logger.debug("Fetching all employees")

        try:
            db_employees = self.db.get_all_employees()
            employees = []

            for emp_data in db_employees:
                employees.append(Employee(
                    full_name=emp_data['full_name'],
                    birth_date=emp_data['birth_date'],
                    gender=emp_data['gender']
                ))

            self.logger.info(f"Fetched {len(employees)} employees")
            return employees

        except Exception as e:
            self.logger.error(f"Failed to fetch employees: {str(e)}")
            raise RuntimeError("Failed to retrieve employees") from e

    def get_male_employees_with_f_surname(self) -> Tuple[List[Employee], float]:
        """
        Получает мужчин с фамилией на 'F' с замером времени

        :return: (Список сотрудников, время выполнения в секундах)
        :raises RuntimeError: При ошибках базы данных
        """
        self.ensure_table_exists()
        self.logger.debug("Querying male employees with F surname")
        return self.db.get_employees_by_gender_and_name_start('Male', 'F')

    def optimize_and_test(self) -> Dict[str, Union[timedelta, float]]:
        """
        Оптимизирует БД и замеряет производительность до/после

        :return: Словарь с результатами {
            'before': timedelta,
            'after': timedelta,
            'improvement': float
        }
        """
        self.ensure_table_exists()

        try:
            # Замер ДО оптимизации
            start = datetime.now()
            self.db.get_employees_by_gender_and_name_start("Male", "F")
            time_before = datetime.now() - start

            # Оптимизация
            self.db.create_indexes()

            # Замер ПОСЛЕ оптимизации
            start = datetime.now()
            self.db.get_employees_by_gender_and_name_start("Male", "F")
            time_after = datetime.now() - start

            improvement = (time_before - time_after) / time_before * 100

            return {
                'before': time_before,
                'after': time_after,
                'improvement': improvement
            }
        except Exception as e:
            self.logger.error(f"Optimization test failed: {str(e)}")
            raise RuntimeError("Failed to perform optimization test") from e

    def generate_test_data(self, count: int = 1000000, special_count: int = 100) -> Dict[str, int]:
        """
        Генерирует тестовые данные

        :param count: Общее количество записей
        :param special_count: Количество специальных записей (мужчины на F)
        :return: Статистика {'total': X, 'special': Y}
        :raises RuntimeError: При ошибках генерации
        """
        from faker import Faker
        import random
        from tqdm import tqdm

        self.ensure_table_exists()
        self.logger.info(f"Generating test data: {count} total, {special_count} special")

        fake = Faker()
        batch_size = 10000
        total_added = 0
        special_added = 0

        try:
            # Основные данные
            for _ in tqdm(range(count // batch_size), desc="Generating data"):
                batch = []
                for _ in range(batch_size):
                    gender = random.choice(['Male', 'Female'])
                    first_name = fake.first_name_male() if gender == 'Male' else fake.first_name_female()
                    last_name = fake.last_name()
                    batch.append({
                        'full_name': f"{last_name} {first_name}",
                        'birth_date': fake.date_of_birth(minimum_age=18, maximum_age=65),
                        'gender': gender
                    })

                added = self.batch_add_employees(batch)
                total_added += added

            # Специальные записи (мужчины на F)
            # На тот случай если рандом не создаст записей начинающихся на F
            special_batch = []
            for _ in range(special_count):
                special_batch.append({
                    'full_name': f"Fake_{fake.last_name()} {fake.first_name_male()}",
                    'birth_date': fake.date_of_birth(minimum_age=18, maximum_age=65),
                    'gender': 'Male'
                })

            special_added = self.batch_add_employees(special_batch)
            total_added += special_added

            self.logger.info(
                f"Test data generation complete. Total: {total_added}, Special: {special_added}"
            )

            return {
                'total': total_added,
                'special': special_added
            }

        except Exception as e:
            self.logger.error(f"Test data generation failed: {str(e)}")
            raise RuntimeError("Failed to generate test data") from e

    def search_employees(self, gender: str, name_start: str) -> Tuple[List[Employee], float]:
        """
        Универсальный поиск сотрудников по критериям

        :param gender: Пол для фильтрации ('Male'/'Female')
        :param name_start: Начальные буквы фамилии
        :return: (Список сотрудников, время выполнения)
        """
        self.ensure_table_exists()
        self.logger.info(f"Searching employees: gender={gender}, name_start={name_start}")

        try:
            db_results, exec_time = self.db.get_employees_by_gender_and_name_start(
                gender=gender,
                name_start=name_start
            )

            employees = [
                Employee(
                    full_name=emp['full_name'],
                    birth_date=emp['birth_date'],
                    gender=emp['gender']
                )
                for emp in db_results
            ]

            return employees, exec_time
        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            raise RuntimeError("Failed to perform search") from e
