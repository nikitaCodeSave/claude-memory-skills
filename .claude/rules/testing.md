# Правила тестирования (ОБЯЗАТЕЛЬНЫЕ)

## Coverage Requirements

**Минимальный порог: 80%** — это НЕ рекомендация, это ТРЕБОВАНИЕ.

```bash
# Проверка coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

## Типы тестов (ВСЕ обязательны)

| Тип | Что тестирует | Инструмент |
|-----|---------------|------------|
| Unit | Отдельные функции, чистая логика | pytest |
| Integration | API, база данных, внешние сервисы | pytest + mocks |
| E2E | Критичные user flows | playwright (если есть UI) |

## TDD Workflow (СТРОГО)

```
1. RED    → Напиши падающий тест
2. RUN    → Подтверди что тест ПАДАЕТ
3. GREEN  → Минимальный код для прохождения
4. RUN    → Подтверди что тест ПРОХОДИТ
5. REFACTOR → Улучши код
6. RUN    → Подтверди что тесты ПРОХОДЯТ
7. COVERAGE → Проверь >= 80%
```

**ЗАПРЕЩЕНО:**
- Писать код ДО теста
- Изменять тесты чтобы они прошли (fix code, not tests!)
- Пропускать запуск тестов после изменений
- Коммитить с падающими тестами
- Коммитить с coverage < 80%

## Quality Checklist

Каждый тест ДОЛЖЕН покрывать:

- [ ] Happy path (нормальная работа)
- [ ] Edge cases (пустые значения, границы, None)
- [ ] Error cases (невалидный ввод, исключения)
- [ ] Boundary conditions (min/max значения)

## Именование тестов

```python
# Паттерн: test_<что_тестируем>_<сценарий>
def test_calculate_total_returns_sum_of_items():
def test_calculate_total_returns_zero_for_empty_list():
def test_calculate_total_raises_on_negative_price():
```

## Изоляция тестов

- Тесты НЕЗАВИСИМЫ друг от друга
- Порядок выполнения НЕ ВАЖЕН
- Каждый тест — своя настройка (Arrange)
- Моки для внешних зависимостей (HTTP, DB, файлы, время)

## Агенты для тестирования

| Агент | Когда использовать |
|-------|-------------------|
| `tdd-test-writer` | RED фаза — писать падающие тесты |
| `tdd-implementer` | GREEN фаза — минимальная реализация |
| `tdd-refactorer` | REFACTOR фаза — улучшение кода |
| `code-reviewer` | После TDD цикла — проверка качества |

## Troubleshooting

**Тесты падают после изменений:**
1. НЕ изменяй тесты (если они корректны)
2. Исправь реализацию
3. Проверь mock-конфигурации
4. Используй `tdd-implementer` агент

**Coverage ниже 80%:**
1. Найди непокрытые строки: `pytest --cov=src --cov-report=term-missing`
2. Добавь тесты для edge cases
3. Проверь все ветки условий

## TDD Antipatterns (ИЗБЕГАТЬ)

| Антипаттерн | Проблема | Решение |
|-------------|----------|---------|
| Testing Implementation Details | Хрупкие тесты | Тестируй поведение, не структуру |
| Overly Complex Tests | Сложно поддерживать | Держи тесты простыми и сфокусированными |
| Skipping Red Phase | Тесты ничего не доказывают | Всегда убедись что тест падает |
| Testing Everything | Потраченное время | Фокус на поведении, не на % |
| Slow Tests | Медленная обратная связь | Unit тесты быстрые (<1s) |
| Brittle Tests | Ложные падения | Избегай over-mocking |
| Test Interdependence | Порядок влияет на результат | Каждый тест независим |
| Assertion Roulette | Непонятно что упало | Одна проверка на тест |

### Признаки плохих тестов

```python
# ПЛОХО: Тестирует реализацию
def test_user_service_calls_repository():
    mock_repo.get.assert_called_once()  # Проверяет КАК, не ЧТО

# ХОРОШО: Тестирует поведение
def test_get_user_returns_user_data():
    result = service.get_user("123")
    assert result.name == "John"  # Проверяет результат
```

```python
# ПЛОХО: Много assertions без смысла
def test_everything():
    assert user.id
    assert user.name
    assert user.email
    assert user.created_at
    # Что именно тестируем?

# ХОРОШО: Один тест — один аспект
def test_user_has_valid_email_format():
    assert "@" in user.email
```
