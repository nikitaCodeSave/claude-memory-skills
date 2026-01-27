---
name: tdd
description: Создание TDD pipeline с отслеживанием задач. Использовать для новых фич, требующих полный Red-Green-Refactor цикл.
allowed-tools: Read, Glob, TaskCreate, TaskUpdate, TaskList
argument-hint: <описание фичи>
auto-triggers:
  - implement
  - add feature
  - build
  - create
  - develop
  - new feature
  - реализовать
  - добавить фичу
  - создать
  - разработать
  - новая фича
  - сделать
---

# TDD Pipeline: $ARGUMENTS

## 1. Проверка Memory Bank

Сначала проверь Memory Bank на похожие фичи и паттерны:

```
Read: .claude/memory/feature-completed.json
Read: .claude/memory/feature-backlog.json
Read: .claude/memory/decisions.json
```

Если есть похожая фича — покажи пользователю:
```
Related features found in Memory Bank:
- feat-001 string_utils: similar validation patterns
- Applicable decisions: dec-001 (Error Handling Strategy)
```

## 2. Создание 5-фазного Task Pipeline

Создай 5 задач с цепочкой зависимостей через TaskCreate:

```
ANALYSIS: Определить requirements для $ARGUMENTS
  - blockedBy: [] (первая задача)
  - metadata: {phase: "analysis", feature: "$ARGUMENTS", pipelineId: "<uuid>"}

RED: Написать падающие тесты для $ARGUMENTS
  - blockedBy: [ANALYSIS]
  - metadata: {phase: "red", feature: "$ARGUMENTS", pipelineId: "<uuid>"}

GREEN: Реализовать минимальный код для $ARGUMENTS
  - blockedBy: [RED]
  - metadata: {phase: "green", feature: "$ARGUMENTS", pipelineId: "<uuid>"}

REFACTOR: Улучшить качество кода $ARGUMENTS
  - blockedBy: [GREEN]
  - metadata: {phase: "refactor", feature: "$ARGUMENTS", pipelineId: "<uuid>"}

VERIFY: 6-фазная верификация $ARGUMENTS
  - blockedBy: [REFACTOR]
  - metadata: {phase: "verify", feature: "$ARGUMENTS", pipelineId: "<uuid>"}
```

После создания задач установи зависимости через TaskUpdate с addBlockedBy.

## 3. Показать статус Pipeline

Используй TaskList и выведи статус:

```
TDD Pipeline создан для: $ARGUMENTS

 ANALYSIS   [pending]     Определить requirements
 RED        [blocked]     Написать падающие тесты
 GREEN      [blocked]     Реализовать минимальный код
 REFACTOR   [blocked]     Улучшить качество кода
 VERIFY     [blocked]     6-фазная верификация

Команды для выполнения каждой фазы:
  /tdd-analyze           → Определить requirements (ПЕРВЫЙ ШАГ!)
  /tdd-red               → Написать падающие тесты
  /tdd-green             → Реализовать для прохождения
  /tdd-refactor          → Улучшить код
  /verify                → Верификация перед коммитом

Текущий статус: ANALYSIS фаза готова к выполнению
```

## 4. Инструкции пользователю

```
ВАЖНО: Начни с /tdd-analyze для определения requirements.
Это гарантирует что тесты покроют все acceptance criteria.

Workflow: ANALYSIS → RED → GREEN → REFACTOR → VERIFY → commit
```

## Memory Bank Integration

При создании pipeline:
1. Проверь feature-backlog.json — если фича уже запланирована, используй её данные
2. Проверь feature-completed.json — найди похожие фичи для reference
3. Проверь decisions.json — применимые design decisions

## Parallel Pipelines

Можно создать несколько pipeline параллельно:
```
/tdd email_validation
/tdd password_validator
```

Каждый pipeline имеет уникальный pipelineId в metadata.
Используй /tdd-status для просмотра всех активных pipelines.

## Примечания
- 5 фаз: ANALYSIS → RED → GREEN → REFACTOR → VERIFY
- Каждая фаза заблокирована предыдущей (blockedBy enforcement)
- Субагенты работают в изолированных контекстах
- Memory Bank сохраняет историю для future reference
- См. `rules/agents.md` для правил делегирования
- См. `rules/memory.md` для работы с Memory Bank
