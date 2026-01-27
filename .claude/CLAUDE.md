# Python TDD Project

## Суть (для любого агента)

- **TDD ОБЯЗАТЕЛЕН:** analysis → тест → код → рефакторинг
- **Coverage >= 80%** — блокирует коммит
- Субагенты работают в изолированных контекстах
- **Memory Bank** — долгосрочная память для patterns и decisions

## Commands

```bash
/tdd <feature>       # Создать 5-фазный pipeline
/tdd-analyze         # ANALYSIS: определить requirements
/tdd-red <feature>   # RED: падающие тесты
/tdd-green           # GREEN: минимальная реализация
/tdd-refactor        # REFACTOR: улучшить код
/verify              # 6-фазная проверка перед PR
/tdd-status          # Статус всех pipelines
/tdd-cleanup         # Архивировать завершённые
/checkpoint          # Human review point
```

## Workflow (5 фаз)

```
/tdd → /tdd-analyze → /tdd-red → /tdd-green → /tdd-refactor → /verify → commit
```

## ЗАПРЕЩЕНО

- Писать код БЕЗ теста
- Пропускать ANALYSIS фазу
- Изменять тесты чтобы прошли
- Коммит с coverage < 80%
- print()/breakpoint() в src/

## Agents

| Agent | Phase | Purpose |
|-------|-------|---------|
| `requirements-analyst` | ANALYSIS | Определение requirements |
| `tdd-test-writer` | RED | Падающие тесты |
| `tdd-implementer` | GREEN | Минимальная реализация |
| `tdd-refactorer` | REFACTOR | Улучшение кода |
| `code-reviewer` | REVIEW | Проверка качества |

**Синтаксис:** natural language, НЕ Task tool.
```
Use the tdd-test-writer subagent to write tests for user authentication.
```

## Memory Bank

```
.claude/memory/
├── feature-backlog.json      # Запланированные фичи
├── feature-completed.json    # Архив завершённых
├── decisions.json            # Design decisions
├── test-patterns.json        # Паттерны тестов
└── requirements/             # Requirements specs
```

**Использование:**
- При `/tdd` проверяй Memory Bank на похожие фичи
- ANALYSIS создаёт requirements spec
- VERIFY архивирует в feature-completed.json
- `/tdd-cleanup` удаляет Tasks, память остаётся

## Quick Testing

```bash
pytest -q --maxfail=1                     # Быстро, стоп на первом падении
pytest --cov=src --cov-fail-under=80      # С проверкой coverage
ruff check . && ruff format .             # Lint + format
```

## Project Structure

```
src/           # Production код
tests/         # Тесты
.claude/
├── memory/    # Long-term Memory Bank
├── agents/    # Субагенты
├── commands/  # Команды
└── skills/    # Skills (workflows)
```

## Правила (модульные)

| Файл | Содержимое |
|------|------------|
| `rules/testing.md` | Требования к тестам, antipatterns, coverage |
| `rules/coding-style.md` | Стиль, лимиты, type hints |
| `rules/agents.md` | Когда и какой агент, изоляция контекста |
| `rules/memory.md` | Работа с Memory Bank |

## Hooks (автоматические)

- **PostToolUse (.py):** ruff format → ruff check → pytest
- **PreToolUse (commit):** tests pass + coverage >= 80%
- **Stop:** сканирование debug statements
