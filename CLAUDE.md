# Claude Memory Skills

Проект для управления памятью между сессиями Claude Code.

## Memory Bank

Контекст проекта хранится в `memory-bank/memory.json` и загружается автоматически при старте сессии.

### Команды

| Команда | Описание |
|---------|----------|
| `/memory` | Просмотреть текущее состояние памяти |
| `/remember <текст>` | Добавить запись в память |
| `/archive` | Архивировать лог, начать новый цикл |

### Примеры

```
/remember Добавлен JWT refresh token
/remember decision: Redis для кеша — быстрее PostgreSQL
/remember bug: Исправлен race condition
/remember focus: Рефакторинг авторизации
```
