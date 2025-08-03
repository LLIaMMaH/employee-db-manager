# -*- coding: utf-8 -*-

import argparse
import sys

from colorama import init, Fore

from cli.interface import EmployeeCLI
from core.manager import EmployeeManager
from core.logging import get_module_logger

init(autoreset=True)
logger = get_module_logger(__name__)


def main():
    # Настройка парсера аргументов
    parser = argparse.ArgumentParser(
        description='Employee Database Management System',
        epilog='Example: app.py 2 "Ivanov Ivan" 1990-05-15 M'
    )
    parser.add_argument(
        'mode',
        type=int,
        nargs='?',
        help='Режим работы (0-интерактивный, 1-создать таблицу и т.д.)'
    )
    parser.add_argument(
        'args',
        nargs='*',
        help='Аргументы для режима'
    )

    # Парсинг аргументов
    if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help'):
        parser.print_help()
        return

    try:
        args = parser.parse_args()
        manager = EmployeeManager()
        cli = EmployeeCLI(manager)

        # Обработка режимов
        if args.mode is None or args.mode == 0:
            cli.interactive_mode()
        elif args.mode == 1:
            manager.ensure_table_exists()
            print(Fore.GREEN + "Таблица сотрудников создана/проверена")
        elif args.mode == 2 and len(args.args) >= 3:
            manager.add_employee(
                full_name=args.args[0],
                birth_date=args.args[1],
                gender_input=args.args[2]
            )
            print(Fore.GREEN + "Сотрудник успешно добавлен")
        elif args.mode == 3:
            employees = manager.get_all_employees()
            cli.display_employees(employees)
        elif args.mode == 4:
            result = manager.generate_test_data()
            print(Fore.GREEN + f"Сгенерировано {result['total']} записей ({result['special']} спецзаписей)")
        elif args.mode == 5:
            employees, time = manager.get_male_employees_with_f_surname()
            cli.display_employees(employees)
            print(Fore.YELLOW + f"\nЗапрос выполнен за {time:.4f} сек.")
        elif args.mode == '6':
            cli._optimize_and_show_results()
            print(Fore.GREEN + "База данных оптимизирована")
        elif args.mode == '7' and len(args.args) >= 2:
            gender = 'Male' if args[0] in ('1', 'M', 'Male') else 'Female'
            name_part = args[1]
            employees, exec_time = manager.search_employees(gender, name_part)
            cli.display_employees(employees)
            print(f"\nЗапрос выполнен за {exec_time:.4f} сек.")
        else:
            print(Fore.RED + "Неверные аргументы или режим")
            parser.print_help()

    except Exception as e:
        error_message = f"Ошибка: {str(e)}"
        logger.error(error_message)
        print(Fore.RED + error_message)
        sys.exit(1)


if __name__ == '__main__':
    main()
