# Claude Code TDD Skills для Python

Production-ready конфигурация `.claude/` для строгого Test-Driven Development в Python проектах.

Эволюционировала из 10+ месяцев интенсивной ежедневной работы с Claude Code.

## Ключевые особенности

- **Строгий TDD** — тесты ДО кода, coverage >= 80% enforcement
- **Изоляция контекста** — каждая фаза TDD в изолированном субагенте
- **Автоматизация** — hooks для auto-format, lint, тестов после каждого изменения
- **Quality Gates** — блокировка коммита при падающих тестах или низком coverage
- **Verification Loop** — 6-фазная проверка перед PR

## Что внутри

```
project/
├── .claude/                          # Claude Code конфигурация
│   ├── CLAUDE.md                     # Проектные правила и enforcement
│   ├── settings.json                 # Hooks и permissions
│   │
│   ├── agents/                       # Специализированные субагенты
│   │   ├── tdd-test-writer.md       # 🔴 RED: падающие тесты
│   │   ├── tdd-implementer.md       # 🟢 GREEN: минимальная реализация
│   │   ├── tdd-refactorer.md        # 🔵 REFACTOR: улучшение кода
│   │   └── code-reviewer.md         # 📋 REVIEW: quality gates
│   │
│   ├── commands/                     # Slash-команды
│   │   ├── tdd-red.md               # /tdd-red <feature>
│   │   ├── tdd-green.md             # /tdd-green
│   │   ├── tdd-refactor.md          # /tdd-refactor
│   │   ├── checkpoint.md            # /checkpoint
│   │   └── verify.md                # /verify
│   │
│   ├── skills/                       # Workflow definitions
│   │   ├── tdd/SKILL.md             # TDD pipeline orchestrator
│   │   ├── tdd-pipeline/SKILL.md    # Task tracking
│   │   └── verification-loop/SKILL.md # 6-phase verification
│   │
│   └── rules/                        # Обязательные правила
│       ├── testing.md               # Coverage 80%, TDD antipatterns
│       ├── coding-style.md          # Лимиты размеров, type hints
│       └── agents.md                # Правила делегирования агентам
│
├── src/                              # Production код (динамический)
├── tests/                            # Тесты (динамический)
├── conftest.py                       # Shared fixtures
└── pyproject.toml                    # Конфигурация проекта
```

## Быстрый старт

### Установка

```bash
# Скопируй .claude/ в свой проект
cp -r .claude/ /path/to/your/project/

# Установи зависимости
pip install pytest pytest-cov ruff
```

### TDD Workflow

```bash
# Полный цикл для новой фичи
/tdd-red user authentication with JWT
/tdd-green
/tdd-refactor
/verify
git commit
```

### Альтернатива: автоматический pipeline

```bash
/tdd user authentication with JWT
```

Создаёт задачи с зависимостями и ведёт через весь цикл.

### Auto-trigger (проактивный TDD)

TDD workflow автоматически активируется на фразы:
- EN: `implement`, `add feature`, `build`, `create`, `develop`, `new feature`
- RU: `реализовать`, `добавить фичу`, `создать`, `разработать`, `новая фича`

## Ключевые концепции

### Агенты

| Агент | Роль | Когда использовать |
|-------|------|-------------------|
| `tdd-test-writer` | Пишет падающие тесты | RED фаза |
| `tdd-implementer` | Минимальная реализация | GREEN фаза |
| `tdd-refactorer` | Улучшает код | REFACTOR фаза |
| `code-reviewer` | Quality gates | После TDD цикла |

### Hooks (автоматизация)

**PostToolUse** — после каждого Write/Edit .py файла:
- Auto-format (ruff format)
- Lint check (ruff check)
- Тесты (pytest)

**PreToolUse** — перед git commit:
- Проверка что все тесты проходят
- Проверка coverage >= 80%

**Stop** — после каждого ответа Claude:
- Сканирование debug statements (print, breakpoint)

### Rules (enforcement)

| Файл | Содержимое |
|------|------------|
| `rules/testing.md` | Coverage 80%, TDD antipatterns, quality checklist |
| `rules/coding-style.md` | Лимиты размеров, type hints, docstrings |
| `rules/agents.md` | Когда какой агент, изоляция контекста |

### Code Style Limits

| Метрика | Лимит |
|---------|-------|
| Длина файла | 200-400 строк |
| Длина функции | 30 строк |
| Длина строки | 100 символов |
| Глубина вложенности | 4 уровня |

### TDD Antipatterns (избегать)

| Антипаттерн | Решение |
|-------------|---------|
| Testing Implementation Details | Тестируй поведение, не структуру |
| Skipping Red Phase | Всегда убедись что тест падает |
| Brittle Tests | Избегай over-mocking |
| Test Interdependence | Каждый тест независим |

### Verification Loop

6-фазная проверка перед PR:

```
1. Lint      → ruff check
2. Format    → ruff format --check
3. Types     → mypy/pyright (если есть)
4. Tests     → pytest + coverage
5. Security  → поиск secrets, debug statements
6. Diff      → review изменённых файлов
```

Запуск: `/verify`

## Интерактивные checkpoints

После каждой фазы TDD доступен выбор:

```
[1] ✅ APPROVE — продолжить к следующей фазе
[2] 🔄 REVISE — внести изменения
[3] 📝 EXPLAIN — объяснить код/тесты
[4] 🔍 REVIEW — показать файлы
[5] ⏪ ROLLBACK — откатить
[6] ❌ ABORT — прервать workflow
```

## Настройка под проект

### settings.json

Отредактируй hooks под свой стек:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write(*.py)|Edit(*.py)",
      "hooks": [{
        "type": "command",
        "command": "your-test-command",
        "timeout": 120
      }]
    }]
  }
}
```

### CLAUDE.md

Добавь специфичные правила:

```markdown
## Project-specific

- FastAPI для API
- SQLAlchemy ORM
- Alembic migrations
```

### rules/testing.md

Настрой coverage threshold:

```markdown
# Измени если нужен другой порог
pytest --cov=src --cov-fail-under=90
```

## Зависимости

```bash
pip install pytest pytest-cov ruff mypy
```

## User Story Format

Структурируй требования перед началом TDD:

```
As a [role], I want to [action], so that [benefit]

Пример:
As a user, I want to validate my email, so that I receive confirmation
```

## Принципы

1. **Test-First** — никакого кода до теста
2. **Изоляция** — test-writer не знает реализацию
3. **Минимализм** — только код для прохождения тестов
4. **Не меняй тесты** — fix code, not tests
5. **Human review** — checkpoints между фазами
6. **Enforcement** — правила не рекомендации, а требования

## Почему субагенты?

Каждая фаза TDD выполняется в изолированном контексте:

- **tdd-test-writer** — не знает как будет написан код
- **tdd-implementer** — видит только тесты, не рассуждения
- **tdd-refactorer** — улучшает не зная "почему так написано"

Это предотвращает "утечку контекста" между фазами.

## Полный workflow

```
/tdd-red <feature>
    ↓
  Тесты ПАДАЮТ ✓
    ↓
/tdd-green
    ↓
  Тесты ПРОХОДЯТ ✓
    ↓
/tdd-refactor
    ↓
  Код улучшен, тесты ПРОХОДЯТ ✓
    ↓
/verify
    ↓
  6 фаз пройдены ✓
    ↓
git commit
    ↓
  Hooks проверяют tests + coverage ✓
```

## Важные заметки

- **Context management**: Субагенты имеют свои 200k токенов контекста
- **Coverage enforcement**: Коммит заблокирован при coverage < 80%
- **Auto-testing**: Тесты запускаются автоматически после каждого изменения .py

---

## License

MIT
