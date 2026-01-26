# Python TDD Project

## Quick Reference

```bash
# TDD Workflow
/tdd-red <feature>    # Написать падающие тесты
/tdd-green            # Минимальная реализация
/tdd-refactor         # Улучшить код
/verify               # 6-фазная проверка
/checkpoint           # Human review point

# Testing
pytest -q --maxfail=1             # Quick, stop on first failure
pytest --cov=src --cov-fail-under=80  # With coverage check

# Quality
ruff check . && ruff format .     # Lint + format
```

## TDD Cycle (STRICT)

```
1. 🔴 RED      → Write failing test FIRST
2. 🟢 GREEN    → Minimal code to pass
3. 🔵 REFACTOR → Improve, tests stay green
```

## Enforcement Rules

**REQUIREMENTS (not suggestions):**
- Coverage >= 80% — blocks commit if lower
- Tests run automatically after every .py change
- Commit blocked on failing tests
- Debug statements (print, breakpoint) scanned automatically

**PROHIBITED:**
- Writing implementation BEFORE test
- Modifying tests to make them pass
- Committing with coverage < 80%
- Leaving print()/breakpoint() in src/

See:
- `rules/testing.md` — требования к тестам
- `rules/coding-style.md` — стиль кода, лимиты
- `rules/agents.md` — правила делегирования агентам

## Agents

| Agent | Phase | Purpose |
|-------|-------|---------|
| `tdd-test-writer` | RED | Write failing tests |
| `tdd-implementer` | GREEN | Minimal implementation |
| `tdd-refactorer` | REFACTOR | Improve code quality |
| `code-reviewer` | REVIEW | Quality gates check |

**Delegation syntax:**
```
Delegate to tdd-test-writer: implement user authentication
```

**When to delegate:** See `rules/agents.md` for detailed criteria.

## Hooks (Automatic)

### PostToolUse (after Write/Edit .py)
- `ruff format` — auto-format
- `ruff check` — lint errors
- `pytest` — run tests

### PreToolUse (before git commit)
- Tests must pass
- Coverage must be >= 80%

### Stop (after each response)
- Scan for debug statements in src/

## Commands

| Command | Description |
|---------|-------------|
| `/tdd <feature>` | Create TDD pipeline with tasks (auto-triggers on "implement", "create", etc.) |
| `/tdd-red <feature>` | RED phase: write failing tests |
| `/tdd-green` | GREEN phase: implement to pass |
| `/tdd-refactor` | REFACTOR phase: improve code |
| `/checkpoint` | Human review point |
| `/verify` | 6-phase verification before PR |

## Verification Loop

Run `/verify` before commit/PR:

```
Phase 1: Lint      → ruff check
Phase 2: Format    → ruff format --check
Phase 3: Types     → mypy (if available)
Phase 4: Tests     → pytest + coverage >= 80%
Phase 5: Security  → scan for secrets, debug statements
Phase 6: Diff      → review changed files
```

## Test Standards

- pytest + conftest.py for fixtures
- Pattern: `test_<function>_<scenario>`
- AAA: Arrange → Act → Assert
- One assertion per test when possible

### TDD Antipatterns (AVOID)

| Antipattern | Solution |
|-------------|----------|
| Testing Implementation Details | Test behavior, not structure |
| Skipping Red Phase | Always see test fail first |
| Brittle Tests | Avoid over-mocking |
| Test Interdependence | Each test is independent |

### User Story Format

```
As a [role], I want to [action], so that [benefit]
```

### Coverage Requirements

| Scope | Requirement |
|-------|-------------|
| Overall | >= 80% |
| Critical paths | 100% |
| Edge cases | Required |
| Error handling | Required |

## Full Workflow

```
/tdd-red <feature>
    ↓
Tests FAIL ✓
    ↓
/tdd-green
    ↓
Tests PASS ✓
    ↓
/tdd-refactor
    ↓
Code improved, tests PASS ✓
    ↓
/verify
    ↓
6 phases passed ✓
    ↓
git commit
    ↓
Hooks verify tests + coverage ✓
```

## Project Structure

```
src/           # Production код (создаётся через TDD)
tests/         # Тесты (создаются в RED фазе)
conftest.py    # Shared fixtures для pytest
pyproject.toml # pytest, coverage, ruff настройки
```

## Code Style Limits

| Metric | Limit |
|--------|-------|
| File length | 200-400 lines |
| Function length | 30 lines |
| Line length | 100 chars |
| Nesting depth | 4 levels |

See `rules/coding-style.md` for naming conventions, type hints, docstrings.

## Auto-Triggers

TDD workflow активируется автоматически на:
- EN: `implement`, `add feature`, `build`, `create`, `develop`, `new feature`
- RU: `реализовать`, `добавить фичу`, `создать`, `разработать`, `новая фича`, `сделать`

## Tips

- Use subagents for isolation between TDD phases
- Run `/verify` periodically in long sessions
- Check `/checkpoint` after each phase for human review
- Coverage < 80% blocks commit — add tests first
- See `rules/agents.md` for delegation criteria
