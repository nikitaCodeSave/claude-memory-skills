# Python TDD Project

## Суть (для любого агента)

- **TDD ОБЯЗАТЕЛЕН:** тест → код → рефакторинг
- **Coverage >= 80%** — блокирует коммит
- Субагенты работают в изолированных контекстах

## Commands

```bash
/tdd-red <feature>   # RED: падающие тесты
/tdd-green           # GREEN: минимальная реализация
/tdd-refactor        # REFACTOR: улучшить код
/verify              # 6-фазная проверка перед PR
/checkpoint          # Human review point
```

## Workflow

```
/tdd-red → /tdd-green → /tdd-refactor → /verify → commit
```

## ЗАПРЕЩЕНО

- Писать код БЕЗ теста
- Изменять тесты чтобы прошли
- Коммит с coverage < 80%
- print()/breakpoint() в src/

## Agents

| Agent | Phase | Purpose |
|-------|-------|---------|
| `tdd-test-writer` | RED | Падающие тесты |
| `tdd-implementer` | GREEN | Минимальная реализация |
| `tdd-refactorer` | REFACTOR | Улучшение кода |
| `code-reviewer` | REVIEW | Проверка качества |

**Синтаксис:** natural language, НЕ Task tool.
```
Use the tdd-test-writer subagent to write tests for user authentication.
```

**Критерии:** см. `rules/agents.md`

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
conftest.py    # Shared fixtures
pyproject.toml # pytest, coverage, ruff
```

## Детали (модульные правила)

| Файл | Содержимое |
|------|------------|
| `rules/testing.md` | Требования к тестам, antipatterns, coverage |
| `rules/coding-style.md` | Стиль, лимиты, type hints |
| `rules/agents.md` | Когда и какой агент, изоляция контекста |

## Hooks (автоматические)

- **PostToolUse (.py):** ruff format → ruff check → pytest
- **PreToolUse (commit):** tests pass + coverage >= 80%
- **Stop:** сканирование debug statements
