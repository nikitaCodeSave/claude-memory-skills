# Evaluation Format для Claude Code Skills

> Спецификация JSON-формата для тестирования Skills в Claude Code

---

## Обзор

Этот формат разработан для описания тестовых сценариев Claude Code Skills. Он основан на [Evaluation-Driven Development](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) от Anthropic, но адаптирован для специфики Skills.

**Важно:** Claude Code не имеет встроенной поддержки этих файлов. Они служат как:
- Документация тестовых сценариев
- Спецификация для ручного тестирования
- Основа для автоматизированных тест-раннеров

---

## Структура JSON

```json
{
  "name": "string (required)",
  "description": "string (required)",
  "skills": ["array of skill names (required)"],
  "query": "string (required)",
  "expected_behavior": ["array of strings (required)"],
  "validation_criteria": {
    // object with validation rules (required)
  }
}
```

---

## Поля спецификации

### `name` (required)
Уникальный идентификатор теста.

```json
"name": "simple-skill-creation"
```

**Правила:**
- Lowercase с дефисами
- Описывает суть теста
- Уникален в пределах директории

---

### `description` (required)
Человекочитаемое описание теста.

```json
"description": "Тест создания простого однофайлового навыка"
```

---

### `skills` (required)
Список навыков, которые должны быть активны для теста.

```json
"skills": ["skill-creator"]
```

**Использование:**
- Указывает какой Skill тестируется
- Может содержать несколько Skills для интеграционных тестов

---

### `query` (required)
Запрос пользователя, который инициирует тест.

```json
"query": "Создай простой навык для генерации git commit сообщений. Навык должен анализировать staged изменения и предлагать conventional commit формат."
```

**Рекомендации:**
- Пишите как реальный запрос пользователя
- Включайте достаточно контекста
- Указывайте конкретные требования

---

### `expected_behavior` (required)
Список ожидаемых действий/результатов.

```json
"expected_behavior": [
  "Создаёт директорию .claude/skills/commit-helper/",
  "Создаёт файл SKILL.md с валидным YAML frontmatter",
  "name содержит только lowercase и дефисы",
  "description включает триггерные слова",
  "Проходит автоматическую валидацию hooks"
]
```

**Назначение:**
- Чеклист для ручной проверки
- Документация ожидаемого поведения
- Основа для автоматических assertions

---

### `validation_criteria` (required)
Объект с машиночитаемыми критериями валидации.

```json
"validation_criteria": {
  "file_exists": ".claude/skills/commit-helper/SKILL.md",
  "frontmatter_valid": true,
  "name_format": "^[a-z0-9-]+$",
  "description_min_length": 50,
  "triggers_present": ["коммит", "commit", "git"]
}
```

---

## Типы validation_criteria

### Проверка файлов

```json
// Один файл
"file_exists": ".claude/skills/my-skill/SKILL.md"

// Несколько файлов/директорий
"files_exist": [
  ".claude/skills/my-skill/SKILL.md",
  ".claude/skills/my-skill/scripts/"
]
```

### Проверка frontmatter

```json
// Валидность YAML
"frontmatter_valid": true

// Формат поля name
"name_format": "^[a-z0-9-]+$"

// Минимальная длина description
"description_min_length": 50

// Наличие триггерных слов
"triggers_present": ["keyword1", "keyword2"]
```

### Проверка структуры

```json
// context: fork настроен
"context_fork": true

// Progressive disclosure используется
"progressive_disclosure": true

// Максимум строк в SKILL.md
"skill_md_lines": {"max": 500}

// Глубина ссылок
"references_depth": 1
```

### Проверка hooks

```json
"hooks_configured": {
  "PreToolUse": true,
  "PostToolUse": true
}
```

### Проверка скриптов

```json
// Скрипты исполняемые
"scripts_executable": true
```

---

## Примеры

### Пример 1: Простой навык

```json
{
  "name": "simple-skill-creation",
  "description": "Тест создания простого однофайлового навыка",
  "skills": ["skill-creator"],
  "query": "Создай простой навык для генерации git commit сообщений.",
  "expected_behavior": [
    "Создаёт директорию .claude/skills/commit-helper/",
    "Создаёт файл SKILL.md с валидным YAML frontmatter",
    "name содержит только lowercase и дефисы"
  ],
  "validation_criteria": {
    "file_exists": ".claude/skills/commit-helper/SKILL.md",
    "frontmatter_valid": true,
    "name_format": "^[a-z0-9-]+$"
  }
}
```

### Пример 2: Навык с hooks

```json
{
  "name": "complex-skill-with-hooks",
  "description": "Тест создания навыка с hooks и валидацией",
  "skills": ["skill-creator"],
  "query": "Создай навык для ревью безопасности с PreToolUse и PostToolUse hooks.",
  "expected_behavior": [
    "Создаёт SKILL.md с hooks конфигурацией",
    "Создаёт scripts/ директорию",
    "PreToolUse hook настроен на matcher 'Read'",
    "Скрипты имеют исполняемые права"
  ],
  "validation_criteria": {
    "files_exist": [
      ".claude/skills/security-review/SKILL.md",
      ".claude/skills/security-review/scripts/"
    ],
    "hooks_configured": {
      "PreToolUse": true,
      "PostToolUse": true
    },
    "scripts_executable": true
  }
}
```

### Пример 3: Многофайловый навык

```json
{
  "name": "multi-file-skill",
  "description": "Тест создания многофайлового навыка с progressive disclosure",
  "skills": ["skill-creator"],
  "query": "Создай навык для обработки PDF с context: fork и reference файлами.",
  "expected_behavior": [
    "Создаёт SKILL.md < 500 строк",
    "Создаёт REFERENCE.md с документацией",
    "context: fork настроен",
    "Ссылки на один уровень глубины"
  ],
  "validation_criteria": {
    "files_exist": [
      ".claude/skills/pdf-processing/SKILL.md",
      ".claude/skills/pdf-processing/REFERENCE.md"
    ],
    "context_fork": true,
    "skill_md_lines": {"max": 500},
    "references_depth": 1
  }
}
```

---

## Как использовать

### Ручное тестирование

1. Прочитать `query` из evaluation файла
2. Вызвать навык с этим запросом
3. Проверить результат по `expected_behavior`
4. Верифицировать `validation_criteria`

### Автоматическое тестирование

```bash
# Пример проверки критериев через bash
echo "=== Проверка validation_criteria ==="

# file_exists
test -f .claude/skills/commit-helper/SKILL.md && echo "✅ file_exists" || echo "❌ file_exists"

# name_format
grep -oP "^name:\s*\K.*" SKILL.md | grep -qE "^[a-z0-9-]+$" && echo "✅ name_format" || echo "❌ name_format"

# triggers_present
grep -qi "commit" SKILL.md && echo "✅ trigger: commit" || echo "❌ trigger: commit"
```

### Python тест-раннер (пример)

```python
import json
import os
import re

def run_evaluation(eval_file: str) -> dict:
    with open(eval_file) as f:
        spec = json.load(f)

    results = {"name": spec["name"], "passed": [], "failed": []}
    criteria = spec["validation_criteria"]

    # file_exists
    if "file_exists" in criteria:
        path = criteria["file_exists"]
        if os.path.exists(path):
            results["passed"].append(f"file_exists: {path}")
        else:
            results["failed"].append(f"file_exists: {path}")

    # files_exist
    if "files_exist" in criteria:
        for path in criteria["files_exist"]:
            if os.path.exists(path):
                results["passed"].append(f"exists: {path}")
            else:
                results["failed"].append(f"missing: {path}")

    # name_format
    if "name_format" in criteria:
        pattern = criteria["name_format"]
        # ... проверка regex

    return results
```

---

## Best Practices

### Написание evaluation

1. **Один тест = один сценарий** — не смешивайте несколько use cases
2. **Реалистичные query** — пишите как реальный пользователь
3. **Конкретные критерии** — избегайте размытых проверок
4. **Покрывайте edge cases** — тестируйте граничные условия

### Организация файлов

```
evaluations/
├── README.md                    # Эта документация
├── simple-skill-creation.json   # Базовый тест
├── complex-skill-with-hooks.json# Тест с hooks
├── multi-file-skill.json        # Тест многофайловой структуры
└── edge-cases/                  # Дополнительные тесты
    ├── invalid-name.json
    └── missing-description.json
```

### Именование

| Паттерн | Пример | Использование |
|---------|--------|---------------|
| `{feature}-creation` | `simple-skill-creation` | Создание чего-либо |
| `{feature}-with-{aspect}` | `complex-skill-with-hooks` | Фича с особенностью |
| `{adjective}-{noun}` | `multi-file-skill` | Описательное название |
| `edge-{case}` | `edge-invalid-yaml` | Граничные случаи |

---

## Расширение формата

Формат можно расширять дополнительными полями:

```json
{
  "name": "...",
  "description": "...",
  "skills": ["..."],
  "query": "...",
  "expected_behavior": ["..."],
  "validation_criteria": {...},

  // Расширения
  "tags": ["unit", "integration", "smoke"],
  "priority": "high",
  "timeout_seconds": 60,
  "setup": {
    "commands": ["mkdir -p test-dir"]
  },
  "teardown": {
    "commands": ["rm -rf test-dir"]
  }
}
```

---

## См. также

- [ANTHROPIC-EVALUATIONS-GUIDE.md](../../../ANTHROPIC-EVALUATIONS-GUIDE.md) — общий гайд по evaluations
- [Demystifying Evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — официальная статья Anthropic
- [Building Evals Cookbook](https://github.com/anthropics/anthropic-cookbook/blob/main/misc/building_evals.ipynb) — примеры от Anthropic
