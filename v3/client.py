# -*- coding: utf-8 -*-

import requests
from datetime import datetime
import sys

BASE_URL = "http://127.0.0.1:8000"

def print_error(message):
    print(f"\n\033[91mОШИБКА: {message}\033[0m")

def print_success(message):
    print(f"\n\033[92m{message}\033[0m")

def print_menu():
    print("\n=== Employee Database ===")
    print("1. Создать таблицу (автоматически при запуске)")
    print("2. Добавить сотрудника")
    print("3. Показать всех сотрудников")
    print("4. Сгенерировать тестовые данные")
    print("5. Найти мужчин с фамилией на F")
    print("6. Оптимизация базы")
    print("0. Выход")
    print("========================")

def print_employees(employees):
    if not employees:
        print("\nНет данных о сотрудниках")
        return

    print("\nСписок сотрудников:")
    print("=" * 65)
    print(f"{'ФИО':<30} | {'Дата рождения':<12} | {'Пол':<6} | Возраст")
    print("-" * 65)

    for emp in employees:
        print(f"{emp['full_name']:<30} | {emp['birth_date']}    | {emp['gender']:<6} | {emp['age']}")

def handle_command(mode, args):
    try:
        if mode == '2' and len(args) >= 3:
            data = {
                "full_name": args[0],
                "birth_date": args[1],
                "gender": args[2]
            }
            response = requests.post(f"{BASE_URL}/employees/", json=data)
            if response.status_code == 201:
                print_success("Сотрудник успешно добавлен")
            else:
                print_error(response.json().get("detail", "Unknown error"))
        elif mode == '3':
            response = requests.get(f"{BASE_URL}/employees/")
            print_employees(response.json())
        elif mode == '4':
            print("Генерируем 1.000.000 записей и 100 записей для 5-го пункта")
            response = requests.post(f"{BASE_URL}/employees/generate-test-data/")
            print_success(response.json()["message"])
        elif mode == '5':
            start_time = datetime.now()
            response = requests.get(f"{BASE_URL}/employees/male-f/")
            execution_time = datetime.now() - start_time

            print_employees(response.json())
            print(f"\nВремя выполнения запроса: {execution_time.total_seconds():.4f} секунд")
        elif mode == '6':
            response = requests.post(f"{BASE_URL}/employees/optimize/")
            if response.status_code == 200:
                result = response.json()
                print_success(result["message"])
                print("\nРезультаты оптимизации:")
                print(f"До оптимизации: {result['optimization_results']['time_before']:.4f} сек.")
                print(f"После оптимизации: {result['optimization_results']['time_after']:.4f} сек.")
                print(f"Ускорение: {result['optimization_results']['improvement']:.1f}%")
        else:
            print_error("Неверные аргументы")
            print("Примеры:")
            print("  client.py 2 'Ivanov Ivan' 1990-05-15 M - добавить сотрудника")
            print("  client.py 3 - вывести всех сотрудников")
            print("  client.py 4 - генерация 1.000.000 записей с 100 записей для 5-го пункта")
            print("  client.py 5 - вывести всех сотрудников мужского пола и у кого ФИО начинается на букву F")
            print("  client.py 6 - выполнить оптимизацию базы")
    except requests.exceptions.RequestException as e:
        print_error(f"Ошибка соединения с сервером: {str(e)}")

def main():
    # Проверка аргументов командной строки
    if len(sys.argv) > 1:
        handle_command(sys.argv[1], sys.argv[2:])
        return

    # Интерактивный режим
    while True:
        print_menu()
        choice = input("Выберите действие: ")

        try:
            if choice == '1':
                print_success("Таблица создается автоматически при запуске сервера")
            elif choice == '2':
                full_name = input("ФИО: ")
                birth_date = input("Дата рождения (YYYY-MM-DD): ")
                gender = input("Пол (M/F): ")
                handle_command('2', [full_name, birth_date, gender])
            elif choice == '3':
                handle_command('3', [])
            elif choice == '4':
                handle_command('4', [])
            elif choice == '5':
                handle_command('5', [])
            elif choice == '6':
                handle_command('6', [])
            elif choice == '0':
                break
            else:
                print_error("Неверный выбор")
        except Exception as e:
            print_error(str(e))

        input("\nНажмите Enter чтобы продолжить...")

if __name__ == '__main__':
    main()
