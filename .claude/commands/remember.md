# /remember — Добавить запись в память

Добавляет новую запись в `memory-bank/memory.json`.

## Использование

```
/remember Добавлен JWT refresh token flow
/remember decision: Используем Redis для кеша — быстрее PostgreSQL
/remember bug: Исправлен race condition в logout
/remember focus: Рефакторинг авторизации
```

## Типы записей

- **task** — выполненная задача (по умолчанию)
- **decision** — архитектурное решение (можно добавить причину через ` — `)
- **bug** — найденный/исправленный баг
- **note** — заметка
- **focus** — обновление текущего фокуса (не добавляет в лог, обновляет focus)

## Инструкции

1. Прочитай `memory-bank/memory.json`
2. Определи тип записи:
   - Если начинается с `decision:`, `bug:`, `note:`, `focus:` — используй этот тип
   - Иначе — тип `task`
3. Для `focus:` — обнови поле `focus` в JSON
4. Для остальных — добавь запись в массив `log`:
   ```json
   {
     "date": "YYYY-MM-DD",
     "type": "task|decision|bug|note",
     "text": "текст записи",
     "reason": "причина (только для decision, после ' — ')"
   }
   ```
5. Сохрани файл
6. Подтверди добавление

## Пример

Ввод: `/remember decision: Redis для sessions — TTL нативно поддерживается`

Результат в log:
```json
{
  "date": "2026-01-17",
  "type": "decision",
  "text": "Redis для sessions",
  "reason": "TTL нативно поддерживается"
}
```
