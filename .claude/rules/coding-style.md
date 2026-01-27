# Правила стиля кода

## Лимиты размеров

| Метрика | Лимит |
|---------|-------|
| Длина файла | 200-400 строк |
| Длина функции | 30 строк |
| Длина строки | 100 символов |
| Глубина вложенности | 4 уровня |

## Python Style

### Именование

```python
# Классы: PascalCase
class UserRepository:
    pass

# Функции/методы: snake_case
def get_user_by_id(user_id: str) -> User:
    pass

# Константы: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Приватные: префикс underscore
def _validate_input(data: dict) -> bool:
    pass
```

### Type Hints (ОБЯЗАТЕЛЬНО)

Все публичные функции ДОЛЖНЫ иметь type hints:

```python
# ХОРОШО
def process_data(input: dict[str, Any]) -> ProcessResult:
    pass

# ПЛОХО
def process_data(input):
    pass
```

### Docstrings

Public API ДОЛЖЕН иметь docstrings:

```python
def get_user(user_id: str) -> User | None:
    """Получить пользователя по ID.

    Args:
        user_id: Уникальный идентификатор пользователя

    Returns:
        User объект если найден, None иначе

    Raises:
        DatabaseError: Если соединение не удалось
    """
    pass
```

### Иммутабельность

Предпочитай immutable структуры данных:

```python
# ХОРОШО: frozen dataclass
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    id: str
    name: str

# ХОРОШО: tuple для неизменяемых последовательностей
def get_valid_statuses() -> tuple[str, ...]:
    return ("active", "pending", "inactive")
```

### Обработка ошибок

```python
# ХОРОШО: Специфичные исключения
class ValidationError(Exception):
    """Raised when input validation fails."""
    pass

def validate(data: dict) -> None:
    if not data:
        raise ValidationError("Data cannot be empty")

# ПЛОХО: Общие исключения
def validate(data):
    if not data:
        raise Exception("Error")  # Слишком общее
```

## Порядок импортов

```python
# 1. Стандартная библиотека
import os
from typing import Any

# 2. Сторонние пакеты
import pytest
from pydantic import BaseModel

# 3. Локальные модули
from src.models import User
from src.services import UserService
```

## Инструменты качества

```bash
# Форматирование
ruff format .

# Линтинг
ruff check . --fix

# Проверка типов
mypy src/
```

## Правила файлов

### Структура файла

```python
"""Module docstring."""

# Imports (в правильном порядке)

# Constants

# Classes

# Functions

# if __name__ == "__main__": (только для CLI скриптов)
```

### Когда разделять файл

Раздели файл если:
- Превышает 400 строк
- Содержит несвязанные классы/функции
- Сложно найти нужный код
- Много циклических импортов

### Именование файлов

```
# ХОРОШО
user_service.py
test_user_service.py
conftest.py

# ПЛОХО
UserService.py      # Не snake_case
user-service.py     # Дефисы вместо underscore
us.py               # Неинформативно
```
