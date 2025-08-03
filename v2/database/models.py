# -*- coding: utf-8 -*-

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Employee:
    """Модель сотрудника с валидацией данных"""
    full_name: str
    birth_date: date
    gender: str

    def __post_init__(self):
        self.full_name = self._normalize_name(self.full_name)
        self.gender = self._normalize_gender(self.gender)

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Приводит ФИО к стандартному формату"""
        return ' '.join(part.capitalize() for part in name.split())

    @staticmethod
    def _normalize_gender(gender: str) -> str:
        """Нормализует ввод пола"""
        gender = gender.lower()
        if gender in ('м', 'm', 'male', '1'):
            return 'Male'
        elif gender in ('ж', 'f', 'female', '2'):
            return 'Female'
        raise ValueError(f"Invalid gender value: {gender}")

    def calculate_age(self) -> int:
        """Вычисляет возраст на текущую дату"""
        today = datetime.now().date()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age
