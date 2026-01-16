---
name: memory-bank
description: |
  Управляет памятью проекта на четырёх уровнях: долгосрочная (фундамент),
  решения (ADR), среднесрочная (планы/беклог) и краткосрочная (сессия).
  Используй при начале сессий, обновлении контекста, просмотре состояния,
  работе с project memory, session context или когда нужно сохранить прогресс.
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash(python3:*)
  - Bash(cat:*)
  - Bash(wc:*)
  - Glob
  - Grep
---

# Skill управления Memory Bank

## Обзор

Этот skill предоставляет инструкции по работе с четырёхуровневой системой памяти.

**Важно**: Для выполнения операций используй slash-команды из `.claude/commands/`:
- `/mb-init` — инициализация
- `/mb-status` — статус и токены
- `/mb-update` — обновление памяти
- `/mb-plan` — создание плана
- `/mb-archive` — архивация progress

## Уровни памяти

### Уровень 1: Долгосрочная память (Фундамент)
**Файлы**: `projectbrief.md`, `techContext.md`, `systemPatterns.md`
**Бюджет**: ~15K токенов

- Редко изменяется (при инициации проекта, крупных изменениях)
- Основные требования, архитектура, технический стек
- Читается при старте сессии через snapshot
- Обновляется только при изменении фундамента проекта

### Уровень 1.5: Архитектурные решения (ADR)
**Файлы**: `decisions.md`
**Бюджет**: ~5K токенов

- Хронологический лог важных решений в формате ADR
- Обновляется при принятии значимых архитектурных решений
- Содержит: контекст, решение, альтернативы, последствия
- Индекс решений в начале файла для быстрой навигации

### Уровень 2: Среднесрочная память (Активная разработка)
**Файлы**: `activeContext.md`, `backlog.json`
**Бюджет**: ~20K токенов

- Обновляется при завершении фичи/спринта
- Текущий фокус, решения, зависимости, очередь задач
- `backlog.json` — локальный кеш задач (не source of truth)
- Читается при начале работы через snapshot

### Уровень 3: Краткосрочная память (Сессия)
**Файлы**: `progress.json`
**Бюджет**: ~10K токенов

- Обновляется часто во время работы
- Текущая задача, лог работы, инсайты, следующие шаги
- Архивируется в `memory-bank/archive/` при завершении трека/спринта

### Snapshot (автогенерируемый)
**Файл**: `snapshot.md`
**Бюджет**: ~2K токенов

- Генерируется автоматически из всех уровней
- Единственный файл, импортируемый в CLAUDE.md
- Содержит краткую сводку: проект, фокус, задачи, блокеры

## Механизм работы

### Автоматика через Hooks

Hooks в `.claude/settings.json` автоматизируют синхронизацию:

| Hook | Matcher | Действие |
|------|---------|----------|
| SessionStart | `startup\|resume` | `--load` → генерирует snapshot, инжектит в контекст |
| PreCompact | `manual\|auto` | `--save` → сохраняет progress перед сжатием |
| Stop | — | `--checkpoint` → обновляет timestamp |
| SessionEnd | — | `--save` → финальное сохранение |
| PostToolUse | `Write\|Edit` | `--refresh-snapshot-if-needed` → обновляет snapshot при изменении файлов memory-bank/ |

**Примечание**: PostToolUse — глобальный хук, срабатывает при любых Write/Edit операциях.
Автоматически валидирует JSON и регенерирует snapshot только для файлов в memory-bank/.

### Скрипт синхронизации

Путь: `.claude/hooks/memory-sync.py`

```bash
# Загрузить snapshot (для SessionStart)
python3 ".claude/hooks/memory-sync.py" --load

# Сохранить прогресс (для PreCompact/SessionEnd)
python3 ".claude/hooks/memory-sync.py" --save --reason precompact

# Лёгкое сохранение (для Stop)
python3 ".claude/hooks/memory-sync.py" --checkpoint

# Обновить snapshot если файл в memory-bank/ (для PostToolUse)
python3 ".claude/hooks/memory-sync.py" --refresh-snapshot-if-needed "path/to/file"

# Архивировать progress
python3 ".claude/hooks/memory-sync.py" --archive

# Показать статус
python3 ".claude/hooks/memory-sync.py" --status

# Инициализировать структуру
python3 ".claude/hooks/memory-sync.py" --init
```

## Протоколы обновления

### После завершения задачи
1. Отметить задачу выполненной в `backlog.json`
2. Добавить в `completedInSession` в `progress.json`
3. Обновить `workLog` с описанием
4. Обновить `nextSteps`

### При принятии архитектурного решения
1. Создать новую запись ADR в `decisions.md`
2. Обновить индекс решений в начале файла
3. При необходимости обновить `systemPatterns.md`

### Перед завершением сессии
1. Сделать сводку работы в `handoffNotes`
2. Обновить "Заметки для следующей сессии" в `activeContext.md`
3. Hooks автоматически вызовут `--save`

### При начале новой фичи/трека
1. Создать новую запись в `backlog.json`
2. Обновить секцию track в `progress.json`
3. Обновить "Текущий фокус" в `activeContext.md`

### При переполнении Tier 3
1. Вызвать `/mb-archive`
2. Старый progress сохранится в `memory-bank/archive/`
3. Новый progress начнётся с чистого листа

## Форматы файлов

### JSON (backlog.json, progress.json)
- Структурированные данные для надёжного парсинга
- Включать timestamps в формате ISO для всех изменений
- Статусы: `backlog`, `ready`, `in-progress`, `review`, `blocked`, `done`
- Приоритеты: `critical`, `high`, `medium`, `low`

### Markdown (*.md)
- Человекочитаемая документация
- Чёткие секции с заголовками ##
- Timestamp "Последнее обновление" в конце

### ADR формат (decisions.md)
```markdown
## ADR-XXX: [Название]
**Дата**: YYYY-MM-DD
**Статус**: proposed | accepted | deprecated | superseded

### Контекст
### Решение
### Альтернативы
### Последствия
```

## Бюджет токенов

| Уровень | Бюджет | Предупреждение |
|---------|--------|----------------|
| Tier 1 | 15K | >12K (80%) |
| Tier 1.5 | 5K | >4K (80%) |
| Tier 2 | 20K | >16K (80%) |
| Tier 3 | 10K | >8K (80%) |
| Snapshot | 2K | — |
| **Итого память** | ~50K | — |
| **Резерв для работы** | ~78K | 60%+ контекста |

## Лучшие практики

1. **Только snapshot в CLAUDE.md** — полные файлы читай по необходимости
2. **JSON для структурированных данных** — надёжнее Markdown таблиц
3. **Timestamps везде** — помогает отслеживать историю
4. **Регулярная архивация** — `/mb-archive` при завершении спринта
5. **Decisions отдельно** — не смешивай с systemPatterns
6. **Следи за бюджетом** — `/mb-status` показывает использование

## Связанные файлы

- `.claude/settings.json` — конфигурация hooks (глобальные)
- `.claude/commands/mb-*.md` — slash-команды
- `memory-bank/` — файлы памяти
- `memory-bank/archive/` — архив старых progress

## Troubleshooting

### Hooks не срабатывают
1. Проверь `/hooks` — зарегистрированы ли hooks?
2. После изменения `settings.json` нужен `/hooks` review или перезапуск сессии
3. Проверь путь к Python: `which python3`

### Snapshot не обновляется
1. Запусти вручную: `python3 .claude/hooks/memory-sync.py --save`
2. Проверь права на запись в `memory-bank/`

### JSON ошибки
1. Валидируй: `python3 -m json.tool memory-bank/backlog.json`
2. Проверь trailing commas — JSON их не поддерживает
3. Проверь кодировку файла (должна быть UTF-8)

### Переполнение бюджета токенов
1. Запусти `/mb-status` для диагностики
2. Архивируй progress: `/mb-archive`
3. Сократи описания в backlog.json