---
description: Обновить Memory Bank — записать задачу, решение, изменить фокус или обновить беклог.
disable-model-invocation: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
---

# Обновление Memory Bank

Обнови Memory Bank. Аргументы: $ARGUMENTS

## Режимы работы

### Интерактивный (по умолчанию)
Если `$ARGUMENTS` пустой, спроси пользователя:
1. Что обновить? (task / decision / focus / backlog / progress)
2. Какие данные записать?

### Non-interactive
Если `$ARGUMENTS` содержит данные, обработай автоматически:

**`/mb-update task "описание"`** → Отметить задачу выполненной
- Добавить в `progress.json → completedInSession`
- Обновить `workLog`
- Очистить `currentTask` если это она

**`/mb-update decision "название: описание"`** → Записать решение
- Добавить в `decisions.md` новый ADR
- Обновить индекс решений

**`/mb-update focus "новый фокус"`** → Сменить фокус
- Обновить `activeContext.md → Текущий фокус`
- Обновить `progress.json → track`

**`/mb-update backlog "задача" [priority]`** → Добавить в беклог
- Создать новый item в `backlog.json`
- Сгенерировать ID

**`/mb-update --auto`** → Автоанализ
- Проверить git diff
- Определить что изменилось
- Предложить обновления

## После обновления
1. Запусти `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/memory-sync.py" --save --reason manual`
2. Покажи что было обновлено
3. Покажи обновлённый snapshot

## Контекст
Текущий git статус:
!`git status --short 2>/dev/null | head -10 || echo "Не git репозиторий"`