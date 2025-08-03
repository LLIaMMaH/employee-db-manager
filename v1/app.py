# -*- coding: utf-8 -*-

import sys
from datetime import datetime

from employee_db import EmployeeDB


def print_error(message):
    """Выводит сообщение об ошибке"""
    print(f"\n\033[91mОШИБКА: {message}\033[0m")


def print_success(message):
    """Выводит сообщение об успехе"""
    print(f"\n\033[92m{message}\033[0m")


def print_menu():
    """Выводит меню программы"""
    print("\n=== Employee Database ===")
    print("1. Создать таблицу")
    print("2. Добавить сотрудника")
    print("3. Показать всех сотрудников")
    print("4. Сгенерировать тестовые данные")
    print("5. Найти мужчин с фамилией на F")
    print("6. Оптимизация базы")
    print("0. Выход")
    print("========================")


def print_employees(employees):
    """Выводит список сотрудников"""
    if not employees:
        print("\nНет данных о сотрудниках")
        return

    print("\nСписок сотрудников:")
    print("=" * 65)
    print(f"{'ФИО':<30} | {'Дата рождения':<12} | {'Пол':<6} | Возраст")
    print("-" * 65)

    for emp in employees:
        print(f"{emp['full_name']:<30} | {emp['birth_date']}    | {emp['gender']:<6} | {emp['age']}")


def handle_command(db, mode, args):
    """Обрабатывает команду из аргументов"""
    try:
        if mode == '1':
            db.create_table()
            print_success("Таблица успешно создана")
        elif mode == '2' and len(args) >= 3:
            if db.add_employee(args[0], args[1], args[2]):
                print_success("Сотрудник успешно добавлен")
        elif mode == '3':
            employees = db.get_all_employees()
            print_employees(employees)
        elif mode == '4':
            print("Генерируем 1.000.000 записей и 100 записей для 5-го пункта")
            count = db.generate_test_data(1000000, 100)
            print_success(f"Добавлено {count} тестовых записей")
        elif mode == '5':
            start_time = datetime.now()
            employees = db.query_male_f()
            execution_time = datetime.now() - start_time

            print_employees(employees)
            print(f"\nВремя выполнения запроса: {execution_time.total_seconds():.4f} секунд")
        elif mode == '6':
            # Замеряем время до оптимизации
            start_time = datetime.now()
            db.query_male_f()
            time_before = datetime.now() - start_time

            # Выполняем оптимизацию
            if db.optimize_database():
                # Замеряем время после оптимизации
                start_time = datetime.now()
                db.query_male_f()
                time_after = datetime.now() - start_time
                print_success("База данных успешно оптимизирована")
                print("\nРезультаты оптимизации:")
                print(f"До оптимизации: {time_before.total_seconds():.4f} сек.")
                print(f"После оптимизации: {time_after.total_seconds():.4f} сек.")
                improvement = (time_before - time_after) / time_before * 100
                print(f"Ускорение: {improvement:.1f}%")
                print("\nСозданы индексы:")
                print("- idx_gender_lastname: для поиска по полу и первой букве фамилии")
                print("- idx_gender: для фильтрации по полу")
                print("- idx_first_letter: для поиска по первой букве фамилии")
        else:
            print_error("Неверные аргументы")
            print("Примеры:")
            print("  app.py 1 - создать таблицу")
            print("  app.py 2 'Ivanov Ivan' 1990-05-15 M - добавить сотрудника")
            print("  app.py 3 - вывести всех сотрудников")
            print("  app.py 4 - генерация 1.000.000 записей с 100 записей для 5-го пункта")
            print("  app.py 5 - вывести всех сотрудников мужского пола и у кого ФИО начинается на букву F")
            print("  app.py 6 - выполнить оптимизацию базы")
    except RuntimeError as e:
        print_error(str(e))


def main():
    db = EmployeeDB()

    # Проверка аргументов командной строки
    if len(sys.argv) > 1:
        handle_command(db, sys.argv[1], sys.argv[2:])
        return

    # Интерактивный режим
    while True:
        print_menu()
        choice = input("Выберите действие: ")

        try:
            if choice == '1':
                db.create_table()
                print_success("Таблица успешно создана")
            elif choice == '2':
                full_name = input("ФИО: ")
                birth_date = input("Дата рождения (YYYY-MM-DD): ")
                gender = input("Пол (M/F): ")
                if db.add_employee(full_name, birth_date, gender):
                    print_success("Сотрудник успешно добавлен")
            elif choice == '3':
                employees = db.get_all_employees()
                print_employees(employees)
            elif choice == '4':
                count = db.generate_test_data(1000000, 100)
                print_success(f"Добавлено {count} тестовых записей")
            elif choice == '5':
                start_time = datetime.now()
                employees = db.query_male_f()
                execution_time = datetime.now() - start_time

                print_employees(employees)
                print(f"\nВремя выполнения запроса: {execution_time.total_seconds():.4f} секунд")
            elif choice == '6':
                start_time = datetime.now()
                db.query_male_f()
                time_before = datetime.now() - start_time

                if db.optimize_database():
                    start_time = datetime.now()
                    db.query_male_f()
                    time_after = datetime.now() - start_time

                    print_success("База данных успешно оптимизирована")
                    print("\nРезультаты оптимизации:")
                    print(f"До оптимизации: {time_before.total_seconds():.4f} сек.")
                    print(f"После оптимизации: {time_after.total_seconds():.4f} сек.")
                    improvement = (time_before - time_after) / time_before * 100
                    print(f"Ускорение: {improvement:.1f}%")

                    print("\nСозданы индексы:")
                    print("- Составной индекс (пол + первая буква фамилии)")
                    print("- Индекс по полу")
                    print("- Индекс по первой букве фамилии")
            elif choice == '0':
                break
            else:
                print_error("Неверный выбор")
        except RuntimeError as e:
            print_error(str(e))

        input("\nНажмите Enter чтобы продолжить...")


if __name__ == '__main__':
    main()
