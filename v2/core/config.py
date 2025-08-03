# -*- coding: utf-8 -*-

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# === Предупреждение, если .env отсутствует ===
if not os.path.exists(".env"):
    print("⚠️  WARNING: .env файл не найден! Используются переменные окружения или значения по умолчанию.")

load_dotenv()


def parse_bool(val: str, default=False) -> bool:
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    # Database
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")

    # # PostgreSQL
    # DB_HOST: str = os.getenv("DB_HOST", "postgres")
    # DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "employees.db")
    # DB_USER: str = os.getenv("DB_USER", "postgres")
    # DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    # DB_SCHEMA: str = os.getenv("DB_SCHEMA", "public")
    # DB_RECONNECT_ATTEMPTS: int = int(os.getenv("DB_RECONNECT_ATTEMPTS", 10))
    # DB_RECONNECT_DELAY: int = int(os.getenv("DB_RECONNECT_DELAY", 3))
    # DB_CONNECT_TIMEOUT: int = int(os.getenv("DB_CONNECT_TIMEOUT", 5))
    # DB_SSL_REQUIRE: bool = parse_bool(os.getenv("DB_SSL_REQUIRE"), True)
    # DB_SSLROOTCERT: str = os.getenv("DB_SSLROOTCERT", "")
    # DB_MINTHREAD: int = int(os.getenv("DB_MINTHREAD", 2))
    # DB_MAXTHREAD: int = int(os.getenv("DB_MAXTHREAD", 4))
    # DB_MAXCONN_TOTAL: int = int(os.getenv("DB_MAXCONN_TOTAL", 50))
    # DB_MONITOR_INTERVAL: int = int(os.getenv("DB_MONITOR_INTERVAL", 300))
    #
    # # Кеш
    # CACHE_TIMEOUT: int = int(os.getenv("CACHE_TIMEOUT", 300))

    # Логирование
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
    LOG_LEVEL_FILE: str = os.getenv("LOG_LEVEL_FILE", "INFO")
    LOG_TO_JSON: bool = parse_bool(os.getenv("LOG_TO_JSON"), False)
    LOG_JSON_FILE: str = os.getenv("LOG_JSON_FILE", "app.json")
    LOG_TO_CONSOLE: bool = parse_bool(os.getenv("LOG_TO_CONSOLE"), True)
    LOG_LEVEL_CONSOLE: str = os.getenv("LOG_LEVEL_CONSOLE", "INFO")
    LOG_ASYNC_LOGGING: bool = parse_bool(os.getenv("LOG_ASYNC_LOGGING"), True)
    LOG_CAPTURE_EXCEPTIONS: bool = parse_bool(os.getenv("LOG_CAPTURE_EXCEPTIONS"), True)
    LOG_ROTATION: str = os.getenv("LOG_ROTATION", "10 MB")
    LOG_RETENTION: str = os.getenv("LOG_RETENTION", "30 days")

    # Отладка
    DEBUG_MODE: bool = parse_bool(os.getenv("DEBUG_MODE"), False)

    # @property
    # def DB_URL(self) -> str:
    #     return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # def validate(self):
    #     errors = []
    #     if not self.DB_HOST:
    #         errors.append("DB_HOST is not set")
    #     if not self.DB_NAME:
    #         errors.append("DB_NAME is not set")
    #     if not self.DB_USER:
    #         errors.append("DB_USER is not set")
    #     if not self.DB_PASSWORD:
    #         errors.append("DB_PASSWORD is not set")
    #     if errors:
    #         raise ValueError(f"Config validation errors: {errors}")


settings = Settings()
# settings.validate()
