---
description: Archive completed TDD pipelines to free context tokens
---

# TDD Cleanup

## Purpose

Archive completed TDD pipelines (where VERIFY is done) to:
- Free ~20k tokens per pipeline
- Keep Task list clean
- Preserve history in Memory Bank

## Step 1: Find Completed Pipelines

```
TaskList: Find all tasks
Filter: VERIFY tasks with status=completed
Group by: pipelineId
```

## Step 2: Verify Memory Bank Archival

For each completed pipeline, check:
- feature-completed.json contains the feature
- requirements/<feat>.json exists
- All metadata preserved

## Step 3: Delete Pipeline Tasks

For each completed pipeline:
```
TaskUpdate: ANALYSIS task → deleted
TaskUpdate: RED task → deleted
TaskUpdate: GREEN task → deleted
TaskUpdate: REFACTOR task → deleted
TaskUpdate: VERIFY task → deleted
```

## Step 4: Report

```
TDD CLEANUP COMPLETE
════════════════════════════════════════════════════════════════

Archived pipelines:
- email_validation (5 tasks deleted)
- password_validator (5 tasks deleted)

Tokens freed: ~40k (estimated)

Memory Bank updated:
- feature-completed.json: 2 features added
- decisions.json: 1 decision added
- test-patterns.json: 3 patterns added

Remaining active pipelines: X
```

## Safety

Before deleting:
1. Confirm VERIFY status is completed
2. Confirm feature is in feature-completed.json
3. Confirm requirements file exists

If any check fails:
```
WARNING: Pipeline <name> not fully archived

Missing:
- [ ] feature-completed.json entry
- [ ] requirements specification

Run /verify first to complete archival.
```

## Manual Cleanup

To delete a specific incomplete pipeline:
```
TaskUpdate: <task_id> → deleted
```

Use with caution - data not in Memory Bank will be lost.
