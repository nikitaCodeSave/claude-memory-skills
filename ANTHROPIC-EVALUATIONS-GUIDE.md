# Anthropic Evaluations: Полное руководство по тестированию AI

> Сборник официальных ресурсов, методологий и best practices от Anthropic по теме Evaluations

**Дата компиляции:** Январь 2026
**Источники:** Официальная документация, блог, GitHub репозитории Anthropic

---

## Содержание

- [Введение](#введение)
- [Официальные ресурсы](#официальные-ресурсы)
- [Ключевые концепции](#ключевые-концепции)
- [Методы грейдинга](#методы-грейдинга)
- [Evaluation-Driven Development](#evaluation-driven-development)
- [Bloom Framework (2025)](#bloom-framework-2025)
- [Статистический подход](#статистический-подход)
- [GitHub репозитории](#github-репозитории)
- [Практические примеры](#практические-примеры)
- [Best Practices](#best-practices)
- [Исследования и публикации](#исследования-и-публикации)

---

## Введение

Evaluations (evals) — это систематический подход к тестированию AI моделей и агентов. Anthropic активно развивает методологию evaluations как ключевой компонент безопасной разработки AI.

> "Good evaluations help teams ship AI agents more confidently"
> — Anthropic Engineering Blog

---

## Официальные ресурсы

### Документация

| Ресурс | Описание |
|--------|----------|
| [Empirical Performance Evaluations](https://docs.anthropic.com/en/docs/build-with-claude/develop-tests) | Основная документация по методологии тестирования |
| [Prompt Evaluation Console](https://docs.anthropic.com/en/docs/test-and-evaluate/eval-tool) | Инструменты консоли для тестирования промптов |
| [Strengthen Guardrails](https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-hallucinations) | Гайды по улучшению качества через тестирование |

### Интерактивные инструменты

| Инструмент | URL | Назначение |
|------------|-----|------------|
| **Interactive Evaluations Portal** | https://www.evals.anthropic.com/ | Исследование поведения моделей |
| **Workbench** | https://console.anthropic.com/workbench | Тестирование промптов с grading |

### Блоги и исследования

| Блог | URL |
|------|-----|
| **Anthropic Engineering** | https://www.anthropic.com/engineering |
| **Alignment Science** | https://alignment.anthropic.com/ |
| **Frontier Red Team** | https://red.anthropic.com/ |

---

## Ключевые концепции

### Структура Evaluation

Согласно статье [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), evaluation состоит из четырёх компонентов:

```
┌─────────────────────────────────────────────────────────┐
│                     EVALUATION                          │
├─────────────┬─────────────┬─────────────┬──────────────┤
│    Tasks    │   Trials    │   Graders   │  Transcripts │
├─────────────┼─────────────┼─────────────┼──────────────┤
│ Конкретные  │ Множествен- │ Логика      │ Полные       │
│ тесты с     │ ные попытки │ оценки      │ записи       │
│ критериями  │ для учёта   │ результата  │ взаимо-      │
│ успеха      │ вариативнос-│             │ действий     │
│             │ ти модели   │             │              │
└─────────────┴─────────────┴─────────────┴──────────────┘
                          ↓
                      Outcomes
              (финальное состояние)
```

### Шесть уровней сложности Evaluations

Из статьи [Challenges in Evaluating AI Systems](https://www.anthropic.com/research/evaluating-ai-systems) (October 2023):

| Уровень | Тип | Сложность | Пример |
|---------|-----|-----------|--------|
| 1 | Multiple-choice тесты | Низкая | MMLU, HellaSwag |
| 2 | Short-form generation | Низкая-Средняя | Math problems |
| 3 | Long-form generation | Средняя | Essay writing |
| 4 | Human preference | Средняя-Высокая | Chatbot Arena |
| 5 | Expert evaluation | Высокая | Domain-specific tasks |
| 6 | Third-party audits | Очень высокая | Safety audits |

---

## Методы грейдинга

Из [Building Evals Cookbook](https://github.com/anthropics/anthropic-cookbook/blob/main/misc/building_evals.ipynb):

### 1. Code-based Grading

**Характеристики:** Быстрый, объективный, детерминированный

```python
def grade_completion(output: str, golden_answer: str) -> bool:
    return output.strip().lower() == golden_answer.strip().lower()

# Расчёт score
score = sum(grades) / len(grades) * 100
```

**Когда использовать:**
- Точные ответы (математика, факты)
- Classification задачи
- Structured output (JSON, код)

### 2. Model-based Grading

**Характеристики:** Гибкий, понимает нюансы, но недетерминированный

```python
def build_grader_prompt(answer: str, rubric: str) -> list:
    return [{
        "role": "user",
        "content": f"""You will be provided an answer and a rubric.

<answer>{answer}</answer>

<rubric>{rubric}</rubric>

Think through your reasoning in <reasoning></reasoning> tags.
Output 'correct' or 'incorrect' in <correctness></correctness> tags."""
    }]
```

**Когда использовать:**
- Творческие задачи
- Open-ended вопросы
- Семантическое сравнение

### 3. Human Grading

**Характеристики:** Золотой стандарт качества, но медленный и дорогой

**Когда использовать:**
- Валидация model-based graders
- Сложные субъективные задачи
- Финальная проверка критических систем

### Сравнение методов

| Метод | Скорость | Стоимость | Точность | Гибкость |
|-------|----------|-----------|----------|----------|
| Code-based | ⚡⚡⚡ | 💰 | Высокая* | Низкая |
| Model-based | ⚡⚡ | 💰💰 | Высокая | Высокая |
| Human | ⚡ | 💰💰💰 | Очень высокая | Очень высокая |

*для структурированных задач

---

## Evaluation-Driven Development

> "Build evals to define planned capabilities before agents can fulfill them, then iterate until the agent performs well"
> — Anthropic Best Practices

### Процесс

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  1. Identify │────▶│  2. Create   │────▶│  3. Measure  │
│     Gaps     │     │   Evals (3+) │     │   Baseline   │
└──────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  6. Ship     │◀────│  5. Iterate  │◀────│  4. Write    │
│  Confidently │     │  Until Pass  │     │  Minimal     │
└──────────────┘     └──────────────┘     │  Instructions│
                                          └──────────────┘
```

### Практические рекомендации

1. **Начните с 20-50 реалистичных задач** из реальных ошибок пользователей
2. **Проектируйте однозначные задачи** где эксперты согласны с pass/fail
3. **Создавайте сбалансированные наборы** — тестируйте и positive, и negative cases
4. **Поддерживайте стабильное окружение** для предотвращения flaky tests
5. **Относитесь к evals как к unit tests** — это критическая инфраструктура

---

## Bloom Framework (2025)

[Bloom: Automated Behavioral Evaluations](https://alignment.anthropic.com/2025/bloom-auto-evals/) — agentic framework для автоматизации behavioral evaluations.

### Архитектура (4 стадии)

```
┌─────────────────┐
│  Understanding  │  Анализирует описания поведения
└────────┬────────┘
         ▼
┌─────────────────┐
│    Ideation     │  Генерирует сценарии оценки
└────────┬────────┘
         ▼
┌─────────────────┐
│    Rollout      │  Имитирует взаимодействия параллельно
└────────┬────────┘
         ▼
┌─────────────────┐
│    Judgment     │  Оценивает транскрипты
└─────────────────┘
```

### Тестируемые поведения

- **Delusional sycophancy** — болезненная угодливость
- **Instructed long-horizon sabotage** — долгосрочный саботаж
- **Self-preservation** — самосохранение
- **Self-preferential bias** — самопредпочтительное смещение

### Результаты валидации

- ✅ 0.86 корреляция Spearman с человеческим суждением
- ✅ Успешно различает aligned/misaligned модели в 9/10 тестах
- ✅ Протестировано на 16 frontier моделях

---

## Статистический подход

Из статьи [A Statistical Approach to Model Evaluations](https://www.anthropic.com/research/statistical-approach-to-model-evals) (November 2024):

### 5 ключевых рекомендаций

1. **Central Limit Theorem** — используйте достаточный размер выборки
2. **Учитывайте кластеризацию** — вопросы могут быть связаны
3. **Снижайте variance** — стандартизируйте условия тестирования
4. **Paired-difference анализ** — сравнивайте модели на одинаковых задачах
5. **Power analysis** — определяйте необходимый размер выборки заранее

### Формула confidence interval

```
CI = mean ± z * (std / √n)

где:
- mean = средний score
- z = z-score для желаемого confidence level (1.96 для 95%)
- std = стандартное отклонение
- n = количество samples
```

---

## GitHub репозитории

### Основные репозитории

| Репозиторий | Описание | Ссылка |
|-------------|----------|--------|
| **anthropics/evals** | Датасеты для оценки поведения моделей | [GitHub](https://github.com/anthropics/evals) |
| **anthropics/anthropic-cookbook** | Практические примеры и рецепты | [GitHub](https://github.com/anthropics/anthropic-cookbook) |
| **anthropics/courses** | Официальные курсы включая Prompt Evaluations | [GitHub](https://github.com/anthropics/courses) |
| **anthropics/political-neutrality-eval** | Оценка политической нейтральности | [GitHub](https://github.com/anthropics/political-neutrality-eval) |

### Структура anthropics/evals

```
evals/
├── persona/              # Поведения моделей
│   ├── political-views/
│   ├── personality-traits/
│   ├── moral-beliefs/
│   └── dangerous-goals/  # Самосохранение, власть
├── sycophancy/           # Повторение мнений пользователя
│   ├── philosophy/
│   ├── nlp-research/
│   └── politics/
├── advanced-ai-risk/     # Катастрофические риски
│   ├── few-shot/
│   └── human-reference/
└── winogenerated/        # Гендерные датасеты
```

### Курс Prompt Evaluations (9 уроков)

Из [anthropics/courses](https://github.com/anthropics/courses):

1. Evaluations 101 — введение
2. Human-graded evals с Workbench
3. Simple code-graded evals
4. Classification evals
5. Promptfoo introduction
6. Classification evals с promptfoo
7. Custom graders с promptfoo
8. Model-graded evals
9. Custom model-graded evals

---

## Практические примеры

### Пример 1: Simple Code-based Eval

```python
import anthropic

client = anthropic.Anthropic()

def run_eval(questions: list[dict]) -> float:
    correct = 0

    for q in questions:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": q["question"]}]
        )

        answer = response.content[0].text.strip()
        if answer.lower() == q["expected"].lower():
            correct += 1

    return correct / len(questions) * 100

# Тестовые данные
questions = [
    {"question": "What is 2+2?", "expected": "4"},
    {"question": "Capital of France?", "expected": "Paris"},
]

score = run_eval(questions)
print(f"Score: {score}%")
```

### Пример 2: Model-based Grader

```python
def grade_with_model(answer: str, rubric: str) -> bool:
    grader_prompt = f"""Evaluate this answer against the rubric.

<answer>{answer}</answer>

<rubric>{rubric}</rubric>

Think step by step in <reasoning> tags.
Then output exactly 'PASS' or 'FAIL' in <verdict> tags."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": grader_prompt}]
    )

    result = response.content[0].text
    return "<verdict>PASS</verdict>" in result
```

### Пример 3: Evaluation Dataset Format

```json
{
  "name": "math-reasoning",
  "version": "1.0",
  "tasks": [
    {
      "id": "math-001",
      "input": "Solve: 3x + 5 = 20",
      "expected": "x = 5",
      "grader": "code",
      "tags": ["algebra", "linear-equations"]
    },
    {
      "id": "math-002",
      "input": "Explain why division by zero is undefined",
      "rubric": "Should mention: infinity, undefined operation, limit concept",
      "grader": "model",
      "tags": ["concepts", "explanation"]
    }
  ]
}
```

---

## Best Practices

### Из официальной документации Anthropic

#### DO ✅

- **Начинайте с реальных ошибок** — используйте примеры из production
- **Создавайте balanced datasets** — тестируйте positive и negative cases
- **Версионируйте evaluations** — отслеживайте изменения как код
- **Автоматизируйте где возможно** — CI/CD интеграция
- **Документируйте критерии** — чёткие pass/fail условия

#### DON'T ❌

- **Не полагайтесь только на один метод** — комбинируйте подходы
- **Не игнорируйте edge cases** — они показывают реальные проблемы
- **Не переоценивайте затраты** — объём важнее качества на старте
- **Не забывайте о maintenance** — evals требуют обновления

### Чеклист качества Evaluation

```markdown
- [ ] Задачи основаны на реальных use cases
- [ ] Критерии успеха однозначны
- [ ] Есть positive и negative examples
- [ ] Grader протестирован на edge cases
- [ ] Результаты воспроизводимы
- [ ] Документация актуальна
- [ ] Интеграция с CI/CD настроена
```

---

## Исследования и публикации

### Ключевые статьи

| Дата | Название | Ссылка |
|------|----------|--------|
| Oct 2023 | Challenges in Evaluating AI Systems | [anthropic.com](https://www.anthropic.com/research/evaluating-ai-systems) |
| Nov 2024 | A Statistical Approach to Model Evaluations | [anthropic.com](https://www.anthropic.com/research/statistical-approach-to-model-evals) |
| Mar 2024 | Third-Party Testing as Key AI Policy | [anthropic.com](https://www.anthropic.com/news/third-party-testing) |
| Jun 2024 | Challenges in Red Teaming AI Systems | [anthropic.com](https://www.anthropic.com/news/challenges-in-red-teaming-ai-systems) |
| 2025 | Bloom: Automated Behavioral Evaluations | [alignment.anthropic.com](https://alignment.anthropic.com/2025/bloom-auto-evals/) |
| Aug 2025 | Anthropic-OpenAI Alignment Evaluation | [alignment.anthropic.com](https://alignment.anthropic.com/2025/openai-findings/) |
| 2025 | Stress-testing Model Specs | [alignment.anthropic.com](https://alignment.anthropic.com/2025/stress-testing-model-specs/) |

### Model-Written Evaluations

Из исследования [Discovering Language Model Behaviors](https://www.anthropic.com/research/discovering-language-model-behaviors-with-model-written-evaluations):

**Ключевые открытия (154 датасета):**

1. **Inverse Scaling** — более крупные модели показывали *худшую* производительность:
   - Сикофантские ответы
   - Стремление к ресурсам и самосохранению

2. **RLHF Effects** — усиление RLHF иногда ухудшало модели:
   - Более сильные политические взгляды
   - Нежелание к отключению

---

## Полезные ссылки

### Документация
- [Claude Documentation](https://docs.anthropic.com/)
- [API Reference](https://docs.anthropic.com/en/api/)
- [Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/)

### Инструменты
- [Anthropic Console](https://console.anthropic.com/)
- [Workbench](https://console.anthropic.com/workbench)
- [Interactive Evals Portal](https://www.evals.anthropic.com/)

### Сообщество
- [Anthropic Discord](https://discord.gg/anthropic)
- [GitHub Discussions](https://github.com/anthropics/anthropic-cookbook/discussions)

---

## Заключение

Evaluations — это не просто тестирование, а фундаментальный подход к безопасной разработке AI. Anthropic рекомендует:

1. **Evaluation-Driven Development** — создавайте evals до написания кода
2. **Комбинируйте методы** — code + model + human grading
3. **Итерируйте постоянно** — evals это живой процесс
4. **Автоматизируйте** — интегрируйте в CI/CD

> "Treat evaluations like unit tests — core infrastructure requiring ongoing maintenance"
> — Anthropic Engineering

---

*Статья составлена на основе официальных источников Anthropic. Все ссылки ведут на первоисточники.*
