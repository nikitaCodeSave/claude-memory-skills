---
description: GREEN phase - implement minimal code to pass tests
---

# GREEN Phase

## Step 1: Check Task Dependencies

```
TaskList: Find GREEN task for this feature pipeline
Check: Is blockedBy empty? (RED must be completed)
```

**If RED not completed:**
```
BLOCKED: GREEN phase cannot start

The RED phase must be completed first.
Tests must be written BEFORE implementation.

Run: /tdd-red <feature>
```

## Step 2: Mark Task In Progress

```
TaskUpdate: GREEN → in_progress
```

## Step 3: Get Test Context

```
Read: Test file from RED phase (from task metadata)
Understand: What behavior tests expect
```

## Step 4: Use tdd-implementer Subagent

**Use the tdd-implementer subagent** to make all failing tests pass:

**Task:** Write minimal implementation to pass all tests.

**Subagent must:**
1. Read test files to understand expected behavior
2. Write ONLY code necessary to pass tests
3. Run tests after each change
4. Stop when all tests pass

## Step 5: Verify Tests Pass

```bash
pytest tests/test_<feature>.py -v
```

Expected: All tests PASS

## Step 6: Mark Task Completed

```
TaskUpdate: GREEN → completed
Metadata: {
  srcFile: "src/<feature>.py",
  testsPass: true
}
```

## Output

```
GREEN Phase Complete

Implementation: src/<feature>.py
All tests PASS

Ready for REFACTOR phase: /tdd-refactor
```

## Rules
- Do NOT modify tests
- Do NOT add extra functionality
- Only minimal, simple code to pass tests
