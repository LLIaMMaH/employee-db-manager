# -*- coding: utf-8 -*-

from fastapi import FastAPI, HTTPException, status
from datetime import datetime
from pydantic import BaseModel
import aiosqlite
from typing import List, Dict, Any

app = FastAPI(
    title="Employee Database API",
    debug=True
)

DATABASE = 'employees.db'


class EmployeeCreate(BaseModel):
    full_name: str
    birth_date: str
    gender: str


async def get_db_connection():
    conn = await aiosqlite.connect(DATABASE)
    conn.row_factory = aiosqlite.Row
    return conn


async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS employees
                         (
                             id INTEGER PRIMARY KEY AUTOINCREMENT,
                             full_name TEXT NOT NULL,
                             birth_date TEXT NOT NULL,
                             gender TEXT NOT NULL
                         )
                         """)
        await db.commit()


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/", status_code=status.HTTP_200_OK)
async def hello():
    menu = {
        "message": "Employee Database API",
        "available_endpoints": {
            "GET /": "Это меню (вы здесь)",
            "POST /employees/": "Добавить сотрудника (требует JSON: full_name, birth_date, gender)",
            "GET /employees/": "Получить всех сотрудников",
            "POST /employees/generate-test-data/": "Сгенерировать тестовые данные (параметры: count, special)",
            "GET /employees/male-f/": "Найти мужчин с фамилией на F",
            "POST /employees/optimize/": "Оптимизировать базу данных"
        },
        "usage_examples": {
            "add_employee": {"url": "/employees/", "method": "POST", "body": {
                "full_name": "Ivanov Ivan",
                "birth_date": "1990-05-15",
                "gender": "M"
            }},
            "generate_data": {"url": "/employees/generate-test-data/?count=1000000&special=100", "method": "POST"}
        }
    }
    return menu


@app.post("/employees/", status_code=status.HTTP_201_CREATED)
async def create_employee(employee: EmployeeCreate):
    try:
        datetime.strptime(employee.birth_date, '%Y-%m-%d')
        gender = 'Male' if employee.gender.lower() in ('м', 'm', 'male', '1') else 'Female'

        async with aiosqlite.connect(DATABASE) as db:
            await db.execute(
                "INSERT INTO employees (full_name, birth_date, gender) VALUES (?, ?, ?)",
                (employee.full_name, employee.birth_date, gender)
            )
            await db.commit()
            return {"message": "Employee added successfully"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/employees/", response_model=List[Dict[str, Any]])
async def get_all_employees():
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
                                  SELECT full_name,
                                         birth_date,
                                         gender,
                                         (strftime('%Y', 'now') - strftime('%Y', birth_date)) -
                                         (strftime('%m-%d', 'now') < strftime('%m-%d', birth_date)) as age
                                  FROM employees
                                  ORDER BY full_name
                                  """)
        employees = await cursor.fetchall()
        return [dict(row) for row in employees]


@app.post("/employees/generate-test-data/")
async def generate_test_data(count: int = 1000000, special: int = 100):
    from random import choice, randint
    from datetime import date, timedelta

    async with aiosqlite.connect(DATABASE) as db:
        # Основные данные
        for i in range(count):
            gender = choice(['Male', 'Female'])
            first_name = f"Name{randint(1, 1000)}"
            last_name = f"Lastname{randint(1, 1000)}"
            birth_date = date.today() - timedelta(days=randint(18 * 365, 65 * 365))
            await db.execute(
                "INSERT INTO employees (full_name, birth_date, gender) VALUES (?, ?, ?)",
                (f"{last_name} {first_name}", birth_date.isoformat(), gender)
            )

        # Специальные записи
        for i in range(special):
            birth_date = date.today() - timedelta(days=randint(18 * 365, 65 * 365))
            await db.execute(
                "INSERT INTO employees (full_name, birth_date, gender) VALUES (?, ?, ?)",
                (f"Fake_{i} Surname", birth_date.isoformat(), 'Male')
            )

        await db.commit()
        return {"message": f"Generated {count + special} test records"}


@app.get("/employees/male-f/", response_model=List[Dict[str, Any]])
async def query_male_f():
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
                                  SELECT full_name,
                                         birth_date,
                                         gender,
                                         (strftime('%Y', 'now') - strftime('%Y', birth_date)) -
                                         (strftime('%m-%d', 'now') < strftime('%m-%d', birth_date)) as age
                                  FROM employees
                                  WHERE gender = 'Male'
                                    AND full_name LIKE 'F%'
                                  """)
        employees = await cursor.fetchall()
        return [dict(row) for row in employees]


@app.post("/employees/optimize/")
async def optimize_database():
    async with aiosqlite.connect(DATABASE) as db:
        # Замер времени до оптимизации
        start_time = datetime.now()
        await db.execute("SELECT 1 FROM employees WHERE gender = 'Male' AND full_name LIKE 'F%' LIMIT 1")
        time_before = datetime.now() - start_time

        # Создание индексов
        await db.execute("""
                         CREATE INDEX IF NOT EXISTS idx_gender_lastname
                             ON employees(gender, substr(full_name, 1, 1))
                         """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_gender ON employees(gender)")
        await db.execute("""
                         CREATE INDEX IF NOT EXISTS idx_first_letter
                             ON employees(substr(full_name, 1, 1))
                         """)
        await db.commit()

        # Замер времени после оптимизации
        start_time = datetime.now()
        await db.execute("SELECT 1 FROM employees WHERE gender = 'Male' AND full_name LIKE 'F%' LIMIT 1")
        time_after = datetime.now() - start_time

        improvement = (time_before.total_seconds() - time_after.total_seconds()) / time_before.total_seconds() * 100

        return {
            "message": "Database optimized successfully",
            "optimization_results": {
                "time_before": time_before.total_seconds(),
                "time_after": time_after.total_seconds(),
                "improvement": improvement
            }
        }
