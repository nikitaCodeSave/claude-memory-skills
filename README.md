# Claude Code TDD Skills для Python

Production-ready конфигурация `.claude/` для строгого Test-Driven Development в Python проектах.

## Ключевые особенности

- **5-фазный TDD** — ANALYSIS → RED → GREEN → REFACTOR → VERIFY
- **Tasks API** — отслеживание прогресса с dependency enforcement
- **Memory Bank** — долгосрочная память для patterns, decisions, requirements
- **Изоляция контекста** — каждая фаза TDD в изолированном субагенте
- **Автоматизация** — hooks для auto-format, lint, тестов после каждого изменения
- **Quality Gates** — блокировка коммита при падающих тестах или coverage < 80%

## Архитектура: Два уровня памяти

```
┌─────────────────────────────────────────────────────────────────┐
│                    ДВУХУРОВНЕВАЯ СИСТЕМА ПАМЯТИ                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  УРОВЕНЬ 1: SESSION MEMORY (Tasks API)                          │
│  - Активные TDD pipelines (in-progress features)                │
│  - Dependency enforcement (blockedBy)                           │
│  - ~20k tokens на pipeline, persist через compaction            │
│  - Очистка через /tdd-cleanup                                   │
│                                                                 │
│  УРОВЕНЬ 2: LONG-TERM MEMORY (JSON Memory Bank)                 │
│  - Git-tracked, persist навсегда                                │
│  - feature-backlog.json — запланированные фичи                  │
│  - feature-completed.json — архив завершённых                   │
│  - decisions.json — design decisions                            │
│  - test-patterns.json — многоразовые паттерны                   │
│  - requirements/ — спецификации требований                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Структура проекта

```
project/
├── .claude/                          # Claude Code конфигурация
│   ├── CLAUDE.md                     # Проектные правила
│   ├── settings.json                 # Hooks и permissions
│   │
│   ├── memory/                       # Long-term Memory Bank
│   │   ├── feature-backlog.json     # Очередь фич
│   │   ├── feature-completed.json   # Архив завершённых
│   │   ├── decisions.json           # Design decisions
│   │   ├── test-patterns.json       # Паттерны тестов
│   │   └── requirements/            # Requirements specs
│   │
│   ├── agents/                       # Специализированные субагенты
│   │   ├── requirements-analyst.md  # ⬜ ANALYSIS: requirements
│   │   ├── tdd-test-writer.md       # 🔴 RED: падающие тесты
│   │   ├── tdd-implementer.md       # 🟢 GREEN: минимальная реализация
│   │   ├── tdd-refactorer.md        # 🔵 REFACTOR: улучшение кода
│   │   └── code-reviewer.md         # 📋 REVIEW: quality gates
│   │
│   ├── commands/                     # Slash-команды
│   │   ├── tdd-analyze.md           # /tdd-analyze
│   │   ├── tdd-red.md               # /tdd-red <feature>
│   │   ├── tdd-green.md             # /tdd-green
│   │   ├── tdd-refactor.md          # /tdd-refactor
│   │   ├── verify.md                # /verify
│   │   ├── tdd-status.md            # /tdd-status
│   │   ├── tdd-cleanup.md           # /tdd-cleanup
│   │   └── checkpoint.md            # /checkpoint
│   │
│   ├── skills/                       # Workflow definitions
│   │   └── tdd/SKILL.md             # TDD pipeline orchestrator
│   │
│   ├── rules/                        # Обязательные правила
│   │   ├── testing.md               # Coverage 80%, TDD antipatterns
│   │   ├── coding-style.md          # Лимиты размеров, type hints
│   │   ├── agents.md                # Правила делегирования
│   │   └── memory.md                # Работа с Memory Bank
│   │
│   └── scripts/
│       └── update-memory.py         # Auto-update Memory Bank
│
├── src/                              # Production код
└── tests/                            # Тесты
```

## Быстрый старт

### Установка

```bash
# Скопируй .claude/ в свой проект
cp -r .claude/ /path/to/your/project/

# Установи зависимости
pip install pytest pytest-cov ruff
```

### 5-фазный TDD Workflow

```bash
# 1. Создать pipeline с 5 задачами
/tdd user authentication

# 2. Определить requirements (ОБЯЗАТЕЛЬНО!)
/tdd-analyze

# 3. Написать падающие тесты
/tdd-red

# 4. Минимальная реализация
/tdd-green

# 5. Улучшить код
/tdd-refactor

# 6. Верификация перед коммитом
/verify

# 7. Коммит (hooks проверят tests + coverage)
git commit
```

### Управление pipelines

```bash
# Статус всех pipelines и Memory Bank
/tdd-status

# Архивировать завершённые (освободить tokens)
/tdd-cleanup
```

## Команды

| Команда | Фаза | Описание |
|---------|------|----------|
| `/tdd <feature>` | — | Создать 5-фазный pipeline |
| `/tdd-analyze` | ANALYSIS | Определить requirements |
| `/tdd-red` | RED | Написать падающие тесты |
| `/tdd-green` | GREEN | Минимальная реализация |
| `/tdd-refactor` | REFACTOR | Улучшить код |
| `/verify` | VERIFY | 6-фазная проверка |
| `/tdd-status` | — | Статус pipelines |
| `/tdd-cleanup` | — | Архивировать завершённые |
| `/checkpoint` | — | Human review point |

## Агенты

| Агент | Фаза | Роль |
|-------|------|------|
| `requirements-analyst` | ANALYSIS | Определение acceptance criteria |
| `tdd-test-writer` | RED | Пишет падающие тесты |
| `tdd-implementer` | GREEN | Минимальная реализация |
| `tdd-refactorer` | REFACTOR | Улучшает код |
| `code-reviewer` | REVIEW | Quality gates |

**Изоляция контекста:** каждый агент работает в изолированном 200k контексте и не видит работу других агентов.

## Memory Bank

### Структура

```
.claude/memory/
├── feature-backlog.json      # Запланированные фичи с приоритетами
├── feature-completed.json    # Архив: coverage, commits, lessons learned
├── decisions.json            # Design decisions с reasoning
├── test-patterns.json        # Многоразовые паттерны тестов
└── requirements/             # Requirements Specifications
    └── feat-XXX.json         # AC-001, AC-002... для каждой фичи
```

### Использование

- При `/tdd` проверяется Memory Bank на похожие фичи
- `/tdd-analyze` создаёт requirements spec с acceptance criteria
- `/verify` архивирует в feature-completed.json
- `/tdd-cleanup` удаляет Tasks, но память остаётся

### Requirements Specification

```json
{
  "feature_id": "feat-003",
  "feature_name": "email_validation",
  "user_story": {
    "role": "user",
    "action": "validate email addresses",
    "benefit": "prevent invalid registrations"
  },
  "acceptance_criteria": [
    {"id": "AC-001", "description": "Valid email passes", "priority": "must"},
    {"id": "AC-002", "description": "Invalid format rejected", "priority": "must"}
  ],
  "edge_cases": ["Empty input", "None input", "Very long email"],
  "out_of_scope": ["DNS MX verification"],
  "technical_constraints": ["No external HTTP calls"]
}
```

## Hooks (автоматизация)

### PostToolUse — после изменения .py файлов

```
ruff format → ruff check → pytest
```

### PreToolUse — перед git commit

```
pytest (все тесты должны пройти)
pytest --cov --cov-fail-under=80 (coverage >= 80%)
```

### Stop — после каждого ответа Claude

```
Сканирование print()/breakpoint() в src/
```

## Правила (enforcement)

| Файл | Содержимое |
|------|------------|
| `rules/testing.md` | Coverage 80%, TDD antipatterns, quality checklist |
| `rules/coding-style.md` | Лимиты размеров, type hints, docstrings |
| `rules/agents.md` | Когда какой агент, изоляция контекста |
| `rules/memory.md` | Работа с Memory Bank |

### Лимиты кода

| Метрика | Лимит |
|---------|-------|
| Длина файла | 200-400 строк |
| Длина функции | 30 строк |
| Длина строки | 100 символов |
| Глубина вложенности | 4 уровня |

## Verification Loop

6-фазная проверка перед PR:

```
1. Lint      → ruff check
2. Format    → ruff format --check
3. Tests     → pytest + coverage
4. Security  → поиск secrets, debug statements
5. Diff      → review изменённых файлов
6. AC Check  → все acceptance criteria покрыты тестами
```

## Трассировка Requirements → Tests

Каждый acceptance criterion должен иметь тест:

```python
class TestEmailValidation:
    """Tests for email_validation (feat-003)"""

    # AC-001: Valid email passes
    def test_valid_email_passes(self):
        """AC-001: valid email format accepted"""
        assert validate_email("user@example.com") is True

    # AC-002: Invalid format rejected
    def test_invalid_format_raises(self):
        """AC-002: invalid format raises ValidationError"""
        with pytest.raises(ValidationError):
            validate_email("not-an-email")
```

## Параллельные pipelines

Можно работать над несколькими фичами одновременно:

```bash
/tdd email_validation
/tdd password_validator

# Каждый pipeline независим
# /tdd-status покажет оба
```

## Принципы

1. **Analysis-First** — сначала requirements, потом тесты
2. **Test-First** — никакого кода до теста
3. **Изоляция** — каждая фаза в отдельном контексте
4. **Минимализм** — только код для прохождения тестов
5. **Не меняй тесты** — fix code, not tests
6. **Memory Bank** — учись на прошлых фичах
7. **Enforcement** — правила не рекомендации, а требования

## Зависимости

```bash
pip install pytest pytest-cov ruff
```

## License

MIT
