# -*- coding: utf-8 -*-
"""
Модуль логирования для проекта. Поддерживает три приёмника: консоль, файл и JSON-файл.
Пример использования:
```python
from core.logging import get_module_logger, set_log_level

logger = get_module_logger(__name__)
logger.info("Сообщение для логирования")
set_log_level("DEBUG")  # Установить уровень логирования
"""

import sys
import re
import os
from pathlib import Path
from typing import Dict, Optional

from loguru import logger
from core.config import settings


class LoggingSetupError(Exception):
    """Исключение для ошибок настройки логирования."""
    pass


def ensure_log_dir(path: str | Path) -> bool:
    """
    Создаёт директорию логов и проверяет возможность записи.

    Args:
        path: Путь к директории логов.

    Returns:
        bool: True, если директория доступна для записи, иначе False.
    """
    path = Path(path)
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / ".test_write"
        with test_file.open("w") as f:
            f.write("test")
        test_file.unlink()
        return True
    except (OSError, PermissionError) as e:
        logger.error(f"Не удалось создать или записать в {path}: {e}")
        return False


def _get_default_log_dir() -> Path:
    """
    Определяет директорию логов.

    Returns:
        Path: Путь к директории логов.
    """
    log_dir = Path(settings.LOG_DIR).expanduser().resolve() if settings.LOG_DIR else Path.cwd() / "logs"
    if ensure_log_dir(log_dir):
        return log_dir
    raise LoggingSetupError(f"Директория логов недоступна: {log_dir}")


def _sensitive_filter(record: Dict) -> bool:
    """
    Фильтрует чувствительные данные.

    Args:
        record: Запись лога.

    Returns:
        bool: True, чтобы пропустить запись.
    """
    sensitive_patterns = [
        r"password\s*=\s*\S+",
        r"token\s*=\s*\S+",
        r"\b\d{16}\b"
    ]
    message = record["message"]
    for pattern in sensitive_patterns:
        message = re.sub(pattern, "****", message)
    record["message"] = message
    return True


def _setup_logger() -> None:
    """
    Настраивает логгер с тремя приёмниками: консоль, файл и JSON.

    Raises:
        LoggingSetupError: Если настройка не удалась.
    """
    global _logger_initialized
    if _logger_initialized:
        logger.debug(f"Пропуск повторной инициализации логгера (PID: {os.getpid()})")
        return

    try:
        log_dir = _get_default_log_dir()
        log_file = log_dir / Path(settings.LOG_FILE).name
        json_log_file = log_dir / Path(settings.LOG_JSON_FILE).name

        if not ensure_log_dir(log_file.parent):
            logger.error(f"Директория {log_file.parent} недоступна, отключаем файловое логирование.")
            settings.LOG_LEVEL_FILE = False
        if not ensure_log_dir(json_log_file.parent):
            logger.error(f"Директория {json_log_file.parent} недоступна, отключаем JSON логирование.")
            settings.LOG_TO_JSON = False

        logger.remove()

        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level:<8}</level> | "
            "<cyan>{module:<30}</cyan> | <cyan>{function:<20}</cyan> | <cyan>{line:<4}</cyan> | "
            "<level>{message}</level>"
        )

        sinks = [
            {
                "sink": sys.stderr,
                "level": settings.LOG_LEVEL_CONSOLE,
                "format": console_format,
                "colorize": True,
                "filter": _sensitive_filter,
                "enqueue": True,
                "backtrace": settings.DEBUG_MODE,
                "diagnose": settings.DEBUG_MODE,
                "enabled": settings.LOG_TO_CONSOLE,
            },
            {
                "sink": str(log_file),
                "level": settings.LOG_LEVEL_FILE,
                "format": (
                    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | "
                    "{module:<30} | {function:<20} | {line:<4} | {message}"
                ),
                "rotation": settings.LOG_ROTATION,
                "retention": settings.LOG_RETENTION,
                "encoding": "utf-8",
                "enqueue": True,
                "compression": "zip",
                "filter": _sensitive_filter,
                "backtrace": settings.DEBUG_MODE,
                "diagnose": settings.DEBUG_MODE,
                "enabled": settings.LOG_LEVEL_FILE is not False,
            },
            {
                "sink": str(json_log_file),
                "level": settings.LOG_LEVEL_FILE,
                "serialize": True,
                "rotation": settings.LOG_ROTATION,
                "retention": settings.LOG_RETENTION,
                "encoding": "utf-8",
                "enqueue": True,
                "compression": "zip",
                "filter": _sensitive_filter,
                "backtrace": settings.DEBUG_MODE,
                "diagnose": settings.DEBUG_MODE,
                "enabled": settings.LOG_TO_JSON,
            },
        ]

        for sink_config in sinks:
            if sink_config.get("enabled", True):
                logger.debug(f"Добавление приёмника: {sink_config['sink']} (PID: {os.getpid()})")
                logger.add(**{k: v for k, v in sink_config.items() if k != "enabled"})

        if settings.LOG_CAPTURE_EXCEPTIONS:
            def log_excepthook(exc_type, exc_value, exc_traceback):
                logger.bind(module="excepthook").opt(exception=(exc_type, exc_value, exc_traceback)).error(
                    "Необработанное исключение"
                )
            sys.excepthook = log_excepthook

        logger.debug(f"Логгер инициализирован, активных приёмников: {len([s for s in sinks if s.get('enabled', True)])} (PID: {os.getpid()})")
        _logger_initialized = True

    except Exception as e:
        print(f"[ERROR] Не удалось настроить логгер: {e}", file=sys.stderr)
        raise LoggingSetupError(f"Ошибка настройки логгера: {e}")


_logger_initialized = False


def init_logger(level: Optional[str] = None) -> None:
    """
    Инициализирует логгер.

    Args:
        level: Уровень логирования ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
    """
    global _logger_initialized
    if not _logger_initialized:
        default_level = level or ("DEBUG" if settings.DEBUG_MODE else "INFO")
        settings.LOG_LEVEL_FILE = default_level.upper()
        settings.LOG_LEVEL_CONSOLE = default_level.upper()
        logger.debug(f"Инициализация логгера с уровнем: {default_level} (PID: {os.getpid()})")
        _setup_logger()


def set_log_level(level: str) -> None:
    """
    Устанавливает уровень логирования.

    Args:
        level: Уровень логирования ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
    """
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if level.upper() not in valid_levels:
        raise ValueError(f"Недопустимый уровень логирования: {level}. Допустимые: {valid_levels}")
    logger.debug(f"Установка уровня логирования: {level.upper()} (PID: {os.getpid()})")
    settings.LOG_LEVEL_FILE = level.upper()
    settings.LOG_LEVEL_CONSOLE = level.upper()
    logger.remove()
    _setup_logger()


def get_module_logger(module_name: Optional[str] = None) -> logger:
    """
    Возвращает логгер, привязанный к модулю.

    Args:
        module_name: Имя модуля. Если None, определяется автоматически.

    Returns:
        Logger: Экземпляр логгера.
    """
    import inspect
    global _logger_initialized
    if not _logger_initialized:
        default_level = "DEBUG" if settings.DEBUG_MODE else "INFO"
        logger.debug(f"Автоматическая инициализация логгера с уровнем: {default_level} (PID: {os.getpid()})")
        init_logger(level=default_level)
    if module_name is None:
        frame = inspect.currentframe().f_back
        module_name = frame.f_globals.get('__name__', 'unknown')
    return logger.bind(module=module_name)


__all__ = ['get_module_logger', 'LoggingSetupError', 'init_logger', 'set_log_level']
