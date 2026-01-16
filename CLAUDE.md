# Конфигурация проекта

## Memory Bank
Этот проект использует систему Memory Bank для сохранения контекста между сессиями.

### Автозагрузка контекста
@memory-bank/snapshot.md

### Slash-команды (в `.claude/commands/`)
| Команда | Описание |
|---------|----------|
| `/mb-status` | Статус и использование токенов |
| `/mb-update` | Обновить память (task/decision/focus) |
| `/mb-plan [цель]` | Создать план разработки |
| `/mb-archive` | Архивировать progress, начать новый |
| `/mb-init` | Инициализировать Memory Bank |

> **Skill** `memory-bank` содержит инструкции и протоколы.
> **Slash-команды** `/mb-*` выполняют конкретные операции.

### Файлы памяти (не импортируются автоматически)
- `memory-bank/projectbrief.md` — основы проекта (Tier 1)
- `memory-bank/techContext.md` — технический стек (Tier 1)
- `memory-bank/systemPatterns.md` — архитектура (Tier 1)
- `memory-bank/decisions.md` — решения ADR (Tier 1.5)
- `memory-bank/activeContext.md` — текущий фокус (Tier 2)
- `memory-bank/backlog.json` — беклог задач (Tier 2)
- `memory-bank/progress.json` — прогресс сессии (Tier 3)

> **Примечание**: Snapshot генерируется автоматически из всех уровней.
> Полные файлы читай по необходимости через `Read` или команды `/mb-*`.

## Правила разработки
- Проверяй snapshot перед началом работы
- Обновляй память после завершения задач: `/mb-update task "описание"`
- Записывай важные решения: `/mb-update decision "название: причина"`
- При переполнении Tier 3: `/mb-archive`