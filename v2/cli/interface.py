# -*- coding: utf-8 -*-

from datetime import datetime
from typing import List

from colorama import init, Fore, Style

from core.manager import EmployeeManager
from database.models import Employee
from core.logging import get_module_logger

init(autoreset=True)


class EmployeeCLI:
    """Класс для взаимодействия через командную строку"""

    def __init__(self, manager: EmployeeManager):
        self.logger = get_module_logger(__name__)
        self.manager = manager

    def interactive_mode(self):
        """Основной интерактивный режим"""
        logger_message = ""
        while True:
            self._print_menu()
            choice = input(Fore.CYAN + "Выберите действие: " + Style.RESET_ALL)

            try:
                if choice == '1':
                    self._create_table()
                elif choice == '2':
                    self._add_employee_interactive()
                elif choice == '3':
                    self._list_employees()
                elif choice == '4':
                    self._generate_test_data()
                elif choice == '5':
                    self._query_male_f()
                elif choice == '6':
                    self._optimize_db()
                elif choice == '7':
                    self._search_by_criteria()
                elif choice == '0':
                    logger_message = "Выход из программы..."
                    self.logger.info(logger_message)
                    print(Fore.YELLOW + logger_message)
                    break
                else:
                    logger_message = "Неверный выбор!"
                    self.logger.error(logger_message)
                    print(Fore.RED + logger_message)
            except Exception as e:
                logger_message = f"Ошибка: {str(e)}"
                self.logger.error(logger_message)
                print(Fore.RED + logger_message)

            input("\nНажмите Enter чтобы продолжить...")

    def _print_menu(self):
        """Выводит главное меню"""
        print(Fore.BLUE + "\n" + "=" * 50)
        print(Fore.GREEN + "СИСТЕМА УПРАВЛЕНИЯ СОТРУДНИКАМИ".center(50))
        print(Fore.BLUE + "=" * 50)
        print(f"{Fore.YELLOW}1{Style.RESET_ALL} - Создать/проверить таблицу")
        print(f"{Fore.YELLOW}2{Style.RESET_ALL} - Добавить сотрудника")
        print(f"{Fore.YELLOW}3{Style.RESET_ALL} - Список всех сотрудников")
        print(f"{Fore.YELLOW}4{Style.RESET_ALL} - Генерация тестовых данных")
        print(f"{Fore.YELLOW}5{Style.RESET_ALL} - Запрос: мужчины на 'F'")
        print(f"{Fore.YELLOW}6{Style.RESET_ALL} - Оптимизировать БД")
        print(f"{Fore.YELLOW}7{Style.RESET_ALL} - Универсальный поиск")
        print(f"{Fore.RED}0{Style.RESET_ALL} - Выход")
        print(Fore.BLUE + "=" * 50)

    def _create_table(self):
        """Создание таблицы"""
        self.manager.ensure_table_exists()
        print(Fore.GREEN + "Таблица сотрудников создана/проверена")

    def _add_employee_interactive(self):
        """Интерактивное добавление сотрудника"""
        print(Fore.GREEN + "\nДОБАВЛЕНИЕ СОТРУДНИКА")

        full_name = input("ФИО (Фамилия Имя Отчество): ").strip()

        while True:
            birth_date = input("Дата рождения (ГГГГ-ММ-ДД): ").strip()
            try:
                datetime.strptime(birth_date, '%Y-%m-%d')
                break
            except ValueError:
                print(Fore.RED + "Неверный формат даты!")

        while True:
            gender = input("Пол (1-М/2-Ж или M/F): ").upper()
            if gender in ['1', 'М', 'M']:
                gender = 'M'
                break
            elif gender in ['2', 'Ж', 'F']:
                gender = 'F'
                break
            else:
                print(Fore.RED + "Введите 1/M для мужчины или 2/F для женщины")

        self.manager.add_employee(full_name, birth_date, gender)
        print(Fore.GREEN + "Сотрудник успешно добавлен!")

    def _list_employees(self):
        """Вывод списка сотрудников"""
        employees = self.manager.get_all_employees()
        self.display_employees(employees)

    def display_employees(self, employees: List[Employee]):
        """Форматированный вывод списка сотрудников"""
        if not employees:
            print(Fore.YELLOW + "Нет данных о сотрудниках")
            return

        print(Fore.BLUE + "\n" + "=" * 70)
        print(Fore.GREEN + "СПИСОК СОТРУДНИКОВ".center(70))
        print(Fore.BLUE + "=" * 70)
        print(f"{Fore.YELLOW}ФИО{' ' * 30}Дата рождения{' ' * 4}Пол{' ' * 4}Возраст")
        print(Fore.BLUE + "-" * 70)

        for emp in employees:
            age = emp.calculate_age()
            print(
                f"{emp.full_name:35} "
                f"{emp.birth_date}   "
                f"{emp.gender:6} "
                f"{age:3} лет"
            )

        print(Fore.BLUE + "=" * 70)
        print(Fore.GREEN + f"Всего: {len(employees)} сотрудников")

    def _generate_test_data(self):
        """Генерация тестовых данных"""
        confirm = input(Fore.RED + "Будет сгенерировано 1 млн записей. Продолжить? (y/n): ")
        if confirm.lower() != 'y':
            return

        result = self.manager.generate_test_data()
        print(Fore.GREEN +
              f"Генерация завершена. Добавлено {result['total']} записей "
              f"(из них {result['special']} мужчин на 'F')")

    def _query_male_f(self):
        """Запрос мужчин с фамилией на F"""
        employees, time = self.manager.get_male_employees_with_f_surname()
        self.display_employees(employees)
        print(Fore.YELLOW + f"\nЗапрос выполнен за {time:.4f} секунд")

    def _optimize_db(self):
        """Оптимизация базы данных"""
        result = self.manager.optimize_and_test()
        print(Fore.GREEN + "База данных успешно оптимизирована")
        print("\nРезультаты оптимизации:")

        # Преобразуем timedelta в секунды с плавающей точкой
        before_sec = result['before'].total_seconds()
        after_sec = result['after'].total_seconds()

        print(f"До оптимизации: {before_sec:.4f} сек.")
        print(f"После оптимизации: {after_sec:.4f} сек.")
        print(f"Ускорение: {result['improvement']:.1f}%")

        print("\nСозданы индексы:")
        print("- idx_gender_fname: для поиска по полу и первой букве фамилии")
        print("- idx_full_name: для поиска по ФИО")
        print("- idx_birth_date: для поиска по дате рождения")

    def _search_by_criteria(self):
        """Поиск сотрудников по критериям"""
        print(Fore.CYAN + "\n=== Поиск сотрудников ===")

        # Ввод пола
        while True:
            gender = input("Пол (1-Male/2-Female): ").strip()
            if gender == '1':
                gender = 'Male'
                break
            elif gender == '2':
                gender = 'Female'
                break
            else:
                print(Fore.RED + "Введите 1 или 2")

        # Ввод начальных букв фамилии
        name_part = input("Начальные буквы фамилии: ").strip()
        if not name_part:
            name_part = '%'  # Если не ввели - ищем любые фамилии

        try:
            # Выполняем поиск
            employees, exec_time = self.manager.search_employees(
                gender=gender,
                name_start=name_part
            )

            self.display_employees(employees)
            print(Fore.YELLOW + f"\nЗапрос выполнен за {exec_time:.4f} сек.")
        except Exception as e:
            print(Fore.RED + f"Ошибка поиска: {str(e)}")
