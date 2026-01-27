# Правила работы с Memory Bank

## Структура Memory Bank

```
.claude/memory/
├── feature-backlog.json      # Очередь запланированных фич
├── feature-completed.json    # Архив завершённых фич
├── decisions.json            # Лог design decisions
├── test-patterns.json        # Многоразовые паттерны тестов
└── requirements/             # Requirements Specifications
    ├── _template.json        # Шаблон
    ├── feat-001.json         # string_utils
    └── feat-002.json         # calculator
```

## Два уровня памяти

### Уровень 1: Session Memory (Tasks API)

- Активные TDD pipelines
- Dependency enforcement (blockedBy)
- ~20k tokens на pipeline
- Очищается через `/tdd-cleanup`

### Уровень 2: Long-Term Memory (JSON файлы)

- Git-tracked, persist навсегда
- Используется при старте новых фич
- Cross-feature references
- Lessons learned

## Когда читать Memory Bank

| Действие | Что читать |
|----------|-----------|
| `/tdd <feature>` | feature-completed, feature-backlog, decisions |
| `/tdd-analyze` | feature-completed (похожие), decisions, test-patterns |
| `/tdd-red` | requirements/<feat>.json, test-patterns |
| `/verify` | Все файлы для архивации |

## Когда писать в Memory Bank

| Действие | Что писать |
|----------|-----------|
| `/tdd-analyze` | requirements/<feat>.json |
| `/verify` (success) | feature-completed.json, decisions.json, test-patterns.json |
| Новое decision | decisions.json |
| Новый паттерн | test-patterns.json |

## Формат Requirements Specification

```json
{
  "feature_id": "feat-XXX",
  "feature_name": "название",
  "user_story": {
    "role": "кто",
    "action": "что делает",
    "benefit": "зачем"
  },
  "acceptance_criteria": [
    {"id": "AC-001", "description": "...", "priority": "must"}
  ],
  "edge_cases": ["..."],
  "out_of_scope": ["..."],
  "dependencies": [{"feature": "...", "reason": "..."}],
  "technical_constraints": ["..."],
  "open_questions": [{"question": "...", "status": "pending"}]
}
```

## Трассировка Requirements → Tests

Каждый acceptance criterion должен иметь тест:

```python
# AC-001: Valid email passes
def test_valid_email_passes(self):
    """AC-001: valid email format accepted"""
    ...
```

## Правила использования

### ДЕЛАЙ

- Проверяй похожие фичи перед началом работы
- Используй существующие test patterns
- Следуй design decisions из decisions.json
- Документируй новые decisions
- Архивируй завершённые фичи

### НЕ ДЕЛАЙ

- Не создавай requirements без согласования
- Не изменяй completed features
- Не удаляй decisions (пометь как deprecated)
- Не дублируй patterns

## Автоматизация

Hook для обновления timestamps при commit:
```bash
python .claude/scripts/update-memory.py
```

## Миграция старых фич

Для фич без requirements (feat-001, feat-002):
- `requirements_ref: null` в feature-completed.json
- При необходимости создай retrospective requirements
