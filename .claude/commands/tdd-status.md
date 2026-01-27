---
description: Show status of all TDD pipelines and Memory Bank
---

# TDD Status

## 1. Active Task Pipelines

```
TaskList: Get all tasks
Group by: pipelineId from metadata
```

Display format:
```
TDD PIPELINES STATUS
════════════════════════════════════════════════════════════════

Pipeline: <feature_name> (pipelineId: xxx-xxx)
┌─────────────┬────────────┬─────────────────────────────────┐
│ Phase       │ Status     │ Details                         │
├─────────────┼────────────┼─────────────────────────────────┤
│  ANALYSIS  │ completed  │ requirements/feat-xxx.json      │
│  RED       │ in_progress│ tests/test_feature.py (8 tests) │
│  GREEN     │ blocked    │ Waiting for RED                 │
│  REFACTOR  │ blocked    │ Waiting for GREEN               │
│  VERIFY    │ blocked    │ Waiting for REFACTOR            │
└─────────────┴────────────┴─────────────────────────────────┘

Pipeline: <another_feature> (pipelineId: yyy-yyy)
...
```

## 2. Memory Bank Summary

```
Read: .claude/memory/feature-backlog.json
Read: .claude/memory/feature-completed.json
Read: .claude/memory/decisions.json
Read: .claude/memory/test-patterns.json
```

Display:
```
MEMORY BANK
════════════════════════════════════════════════════════════════

Backlog:         X features planned
Completed:       Y features archived
Decisions:       Z design decisions
Test Patterns:   W reusable patterns

Recent completions:
- feat-001 string_utils (2025-01-25) - 88% coverage
- feat-002 calculator (2025-01-26) - 85% coverage

Upcoming (from backlog):
- feat-003 email_validation (priority 1)
- feat-004 password_validator (priority 2)
```

## 3. Quick Actions

```
Available commands:
  /tdd <feature>      Create new pipeline
  /tdd-analyze        ANALYSIS phase
  /tdd-red            RED phase
  /tdd-green          GREEN phase
  /tdd-refactor       REFACTOR phase
  /verify             Verification
  /tdd-cleanup        Archive completed pipelines
```

## 4. Token Estimate

```
Active pipelines: X
Estimated tokens: ~Y (X pipelines * ~20k per pipeline)

Tip: Run /tdd-cleanup to archive completed pipelines and free tokens.
```
