---
description: REFACTOR phase - improve code quality while keeping tests green
---

# REFACTOR Phase

## Step 1: Check Task Dependencies

```
TaskList: Find REFACTOR task for this feature pipeline
Check: Is blockedBy empty? (GREEN must be completed)
```

**If GREEN not completed:**
```
BLOCKED: REFACTOR phase cannot start

The GREEN phase must be completed first.
Code must pass all tests before refactoring.

Run: /tdd-green
```

## Step 2: Mark Task In Progress

```
TaskUpdate: REFACTOR → in_progress
```

## Step 3: Use tdd-refactorer Subagent

**Use the tdd-refactorer subagent** to improve code quality:

**Task:** Improve code quality without changing behavior.

**Subagent must:**
1. Identify refactoring opportunities
2. Make ONE change at a time
3. Run tests after EACH change
4. Continue while tests stay green

## Step 4: Refactoring Checklist

- [ ] Extract helper functions
- [ ] Improve naming
- [ ] Remove duplication
- [ ] Add type hints
- [ ] Simplify logic
- [ ] Add docstrings to public API

## Step 5: Verify Tests Still Pass

```bash
pytest tests/test_<feature>.py -v
```

Expected: All tests still PASS

## Step 6: Mark Task Completed

```
TaskUpdate: REFACTOR → completed
Metadata: {
  improvements: ["Added type hints", "Extracted helper function"...],
  testsPass: true
}
```

## Output

```
REFACTOR Phase Complete

Improvements made:
- Added type hints
- Extracted _validate_input() helper
- Improved error messages

All tests still PASS

Ready for VERIFY phase: /verify
```

## Rules
- Tests must pass after EACH change
- No new functionality
- No "while I'm here" changes
