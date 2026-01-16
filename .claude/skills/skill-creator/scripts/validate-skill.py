#!/usr/bin/env python3
"""
Валидатор навыков для Claude Code
Проверяет SKILL.md файлы на соответствие официальной спецификации.
"""

import sys
import re
import json
import os
from pathlib import Path

# ANSI цвета для вывода
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Константы валидации
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_SKILL_LINES = 500
RESERVED_WORDS = ['anthropic', 'claude']
VALID_FRONTMATTER_FIELDS = {
    'name', 'description', 'allowed-tools', 'model', 'context',
    'agent', 'hooks', 'user-invocable', 'disable-model-invocation'
}


def extract_frontmatter(content: str) -> tuple[dict | None, str, list[str]]:
    """Извлечь YAML frontmatter из содержимого SKILL.md."""
    errors = []

    if not content.startswith('---'):
        errors.append("Frontmatter должен начинаться с '---' на строке 1")
        return None, content, errors

    # Найти закрывающий ---
    lines = content.split('\n')
    end_index = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_index = i
            break

    if end_index == -1:
        errors.append("Frontmatter должен заканчиваться '---'")
        return None, content, errors

    frontmatter_text = '\n'.join(lines[1:end_index])
    body = '\n'.join(lines[end_index + 1:])

    # Улучшенный парсер YAML с поддержкой списков
    frontmatter = {}
    current_key = None
    current_value = []
    is_list = False
    is_multiline = False  # Флаг для multiline строк с |

    for line in frontmatter_text.split('\n'):
        if not line.strip():
            continue

        # Проверка на табы
        if '\t' in line:
            errors.append(f"Табы запрещены в YAML, используй пробелы: '{line[:50]}...'")

        # Новый ключ верхнего уровня
        match = re.match(r'^(\w[\w-]*)\s*:\s*(.*)$', line)
        if match:
            # Сохранить предыдущий ключ
            if current_key:
                if is_list:
                    frontmatter[current_key] = current_value if current_value else []
                else:
                    frontmatter[current_key] = '\n'.join(current_value).strip() if current_value else True

            current_key = match.group(1)
            value = match.group(2).strip()

            # Проверка inline-списка [item1, item2]
            if value.startswith('[') and value.endswith(']'):
                inner = value[1:-1].strip()
                if inner:
                    current_value = [item.strip().strip('"').strip("'") for item in inner.split(',')]
                else:
                    current_value = []
                is_list = True
                is_multiline = False
            elif value == '|':
                # Multiline строка — всё после | это текст, не список
                current_value = []
                is_list = False
                is_multiline = True
            elif value == '':
                # Пустое значение — следующие строки могут быть списком
                current_value = []
                is_list = False
                is_multiline = False
            else:
                current_value = [value]
                is_list = False
                is_multiline = False

        # Элемент списка (строка начинается с "  - "), но только если не в multiline режиме
        elif current_key and re.match(r'^\s+-\s+', line) and not is_multiline:
            item = re.sub(r'^\s+-\s+', '', line).strip()
            if not is_list:
                is_list = True
                current_value = []
            current_value.append(item)

        # Продолжение многострочного значения (в том числе с bullet points)
        elif current_key and line.startswith('  ') and (is_multiline or not is_list):
            current_value.append(line[2:])  # Сохраняем отступ после первых 2 пробелов

    # Сохранить последний ключ
    if current_key:
        if is_list:
            frontmatter[current_key] = current_value if current_value else []
        else:
            frontmatter[current_key] = '\n'.join(current_value).strip() if current_value else True

    return frontmatter, body, errors


def validate_name(name: str | None) -> list[str]:
    """Валидация поля 'name'."""
    errors = []

    if not name:
        errors.append("Обязательное поле 'name' отсутствует")
        return errors

    if len(name) > MAX_NAME_LENGTH:
        errors.append(f"Имя превышает {MAX_NAME_LENGTH} символов: {len(name)}")

    if not re.match(r'^[a-z0-9-]+$', name):
        errors.append(f"Имя должно содержать только строчные буквы, цифры и дефисы: '{name}'")

    if name.startswith('-') or name.endswith('-'):
        errors.append("Имя не может начинаться или заканчиваться дефисом")

    for word in RESERVED_WORDS:
        if word in name.lower():
            errors.append(f"Имя содержит зарезервированное слово: '{word}'")

    if '<' in name or '>' in name:
        errors.append("Имя не может содержать XML-теги")

    return errors


def validate_description(description: str | None) -> list[str]:
    """Валидация поля 'description'."""
    errors = []

    if not description:
        errors.append("Обязательное поле 'description' отсутствует")
        return errors

    if len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(f"Описание превышает {MAX_DESCRIPTION_LENGTH} символов: {len(description)}")

    if len(description) < 20:
        errors.append("Описание слишком короткое (рекомендуется минимум 20 символов)")

    if '<' in description or '>' in description:
        errors.append("Описание не может содержать XML-теги")

    # Проверка триггерных слов (предупреждение, не ошибка)
    trigger_indicators_ru = ['используй когда', 'триггер', 'когда пользователь', 'при работе с']
    trigger_indicators_en = ['use when', 'trigger', 'when user', 'when working']
    all_triggers = trigger_indicators_ru + trigger_indicators_en

    has_triggers = any(ind in description.lower() for ind in all_triggers)
    if not has_triggers:
        errors.append(f"{YELLOW}[ПРЕДУПРЕЖДЕНИЕ]{RESET} Описание должно содержать триггерные слова (КОГДА использовать)")

    return errors


def validate_frontmatter_fields(frontmatter: dict) -> list[str]:
    """Валидация имён полей frontmatter."""
    errors = []

    unknown_fields = set(frontmatter.keys()) - VALID_FRONTMATTER_FIELDS
    if unknown_fields:
        errors.append(f"Неизвестные поля frontmatter (будут проигнорированы): {unknown_fields}")

    # Валидация поля context
    if 'context' in frontmatter and frontmatter['context'] != 'fork':
        errors.append(f"Недопустимое значение 'context': '{frontmatter['context']}' (поддерживается только 'fork')")

    # Валидация: agent требует context: fork
    if 'agent' in frontmatter and frontmatter.get('context') != 'fork':
        errors.append("Поле 'agent' требует 'context: fork'")

    return errors


def validate_body(body: str) -> list[str]:
    """Валидация Markdown-содержимого."""
    errors = []

    lines = body.split('\n')
    if len(lines) > MAX_SKILL_LINES:
        errors.append(f"{YELLOW}[ПРЕДУПРЕЖДЕНИЕ]{RESET} Содержимое превышает {MAX_SKILL_LINES} строк ({len(lines)}). Рассмотри разделение на reference-файлы.")

    # Проверка на Windows-пути
    windows_path_pattern = r'[a-zA-Z]:\\|\\[a-zA-Z]'
    if re.search(windows_path_pattern, body):
        errors.append("Обнаружены Windows-пути. Используй прямые слэши (Unix-стиль)")

    return errors


def validate_directory_structure(skill_path: Path, frontmatter: dict | None) -> list[str]:
    """Валидация структуры директории навыка."""
    errors = []

    skill_dir = skill_path.parent

    # Проверка регистрозависимого имени SKILL.md
    if skill_path.name != 'SKILL.md':
        errors.append(f"Файл должен называться 'SKILL.md' (регистрозависимо), получено: '{skill_path.name}'")

    # Проверка совпадения имени директории с полем name
    if frontmatter and frontmatter.get('name'):
        skill_dir_name = skill_dir.name
        if frontmatter['name'] != skill_dir_name:
            errors.append(f"{YELLOW}[ПРЕДУПРЕЖДЕНИЕ]{RESET} Имя '{frontmatter['name']}' не совпадает с директорией '{skill_dir_name}'")

    # Проверка исполняемости скриптов
    scripts_dir = skill_dir / 'scripts'
    if scripts_dir.exists():
        for script in scripts_dir.iterdir():
            if script.is_file() and script.suffix in ['.py', '.sh']:
                if not os.access(script, os.X_OK):
                    errors.append(f"{YELLOW}[ПРЕДУПРЕЖДЕНИЕ]{RESET} Скрипт не исполняемый: {script.name}")

    return errors


def validate_skill(file_path: str) -> tuple[bool, list[str], list[str]]:
    """Основная функция валидации."""
    all_errors = []

    path = Path(file_path)

    # Проверка существования файла
    if not path.exists():
        return False, [f"Файл не найден: {file_path}"]

    # Чтение содержимого
    try:
        content = path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Не удалось прочитать файл: {e}"]

    # Извлечение и валидация frontmatter
    frontmatter, body, parse_errors = extract_frontmatter(content)
    all_errors.extend(parse_errors)

    # Валидация структуры директории
    all_errors.extend(validate_directory_structure(path, frontmatter))

    if frontmatter:
        # Валидация отдельных полей
        all_errors.extend(validate_name(frontmatter.get('name')))
        all_errors.extend(validate_description(frontmatter.get('description')))
        all_errors.extend(validate_frontmatter_fields(frontmatter))

    # Валидация содержимого
    all_errors.extend(validate_body(body))

    # Разделение ошибок и предупреждений
    errors = [e for e in all_errors if '[ПРЕДУПРЕЖДЕНИЕ]' not in e and '[WARNING]' not in e]
    warnings = [e for e in all_errors if '[ПРЕДУПРЕЖДЕНИЕ]' in e or '[WARNING]' in e]

    return len(errors) == 0, errors, warnings


def print_banner(file_path: str):
    """Вывод баннера."""
    print(f"\n{BLUE}{'═' * 60}{RESET}")
    print(f"{BLUE}  Валидация навыка{RESET}")
    print(f"{BLUE}{'═' * 60}{RESET}")
    print(f"  Файл: {file_path}")
    print(f"{BLUE}{'─' * 60}{RESET}\n")


def main():
    """Точка входа."""
    if len(sys.argv) < 2:
        print(f"{YELLOW}Использование: validate-skill.py <путь-к-SKILL.md>{RESET}")
        sys.exit(1)

    # Обработка JSON-ввода от hook
    file_path = sys.argv[1]
    if file_path.startswith('{'):
        try:
            data = json.loads(file_path)
            file_path = data.get('file_path', '')
        except json.JSONDecodeError:
            pass

    # Валидировать только SKILL.md файлы
    if os.path.basename(file_path) != 'SKILL.md':
        sys.exit(0)

    print_banner(file_path)

    is_valid, errors, warnings = validate_skill(file_path)

    # Вывод ошибок
    for error in errors:
        print(f"  {RED}✗{RESET}  {error}")

    # Вывод предупреждений
    for warning in warnings:
        print(f"  {YELLOW}⚠{RESET}  {warning}")

    print()

    if is_valid:
        if warnings:
            print(f"  {GREEN}✓ Навык валиден{RESET} {YELLOW}(с предупреждениями: {len(warnings)}){RESET}")
        else:
            print(f"  {GREEN}✓ Навык валиден!{RESET}")
        print(f"\n{BLUE}{'═' * 60}{RESET}\n")
        sys.exit(0)
    else:
        print(f"  {RED}✗ Валидация не пройдена ({len(errors)} ошибок){RESET}")
        print(f"\n{BLUE}{'═' * 60}{RESET}\n")
        sys.exit(2)  # Код 2 блокирует инструмент в Claude Code hooks


if __name__ == '__main__':
    main()
