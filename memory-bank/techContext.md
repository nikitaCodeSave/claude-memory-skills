# Технический контекст

## Технологический стек

### Языки программирования
- Основной: Markdown (SKILL.md файлы)
- Дополнительные: Python (hooks, скрипты), YAML (frontmatter)

### Фреймворки и библиотеки
| Категория | Технология | Версия | Назначение |
|-----------|------------|--------|------------|
| Runtime | Claude Code | 2.1.9+ | Среда выполнения skills |
| Scripts | Python | 3.10+ | Hooks и синхронизация |
| Data | JSON | — | Структурированные данные (backlog, progress) |

### Инфраструктура
- **Деплой**: Локально в проекте пользователя
- **CI/CD**: Нет (manual)
- **Мониторинг**: `/mb-status` команда

## Структура проекта
```
Skills/
├── CLAUDE.md                    # Конфигурация проекта
├── memory-bank/                 # Файлы памяти
│   ├── snapshot.md              # Автогенерируемая сводка
│   ├── projectbrief.md          # Tier 1: основы
│   ├── techContext.md           # Tier 1: стек
│   ├── systemPatterns.md        # Tier 1: архитектура
│   ├── decisions.md             # Tier 1.5: ADR
│   ├── activeContext.md         # Tier 2: фокус
│   ├── backlog.json             # Tier 2: беклог
│   ├── progress.json            # Tier 3: сессия
│   └── archive/                 # Архив progress
├── plan/                        # Планы и документация
│   └── memory-bank-system/      # Документация Memory Bank
└── .claude/
    ├── settings.json            # Hooks и permissions
    ├── skills/                  # Skills
    │   ├── memory-bank/         # Управление памятью
    │   ├── skill-creator/       # Создание skills
    │   └── reading-gmail/       # Чтение Gmail
    ├── commands/                # Slash-команды /mb-*
    └── hooks/
        └── memory-sync.py       # Скрипт синхронизации
```

## Окружение разработчика
- **Python**: >= 3.10
- **Claude Code**: >= 2.1.9

### Команды настройки
```bash
# Инициализация Memory Bank
/mb-init

# Проверка статуса
/mb-status

# Обновление памяти
/mb-update task "описание"
```

## Внешние зависимости
| Сервис | Назначение | Переменная окружения |
|--------|------------|---------------------|
| Chrome (опционально) | reading-gmail skill | — |

## Ограничения
- Skills работают только в Claude Code CLI
- Memory Bank требует Python 3.10+
- Максимальный бюджет токенов ~50K

---
*Этот файл — часть Memory Bank Tier 1 (Долгосрочная память). Обновляется при изменении стека.*
