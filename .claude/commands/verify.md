---
description: Run 6-phase verification before PR/commit
allowed-tools: Read, Glob, Grep, Bash, TaskList, TaskUpdate
---

# Verification Loop

## Step 1: Check Task Dependencies

```
TaskList: Find VERIFY task for this feature pipeline
Check: Is blockedBy empty? (REFACTOR must be completed)
```

**If REFACTOR not completed:**
```
BLOCKED: VERIFY phase cannot start

The REFACTOR phase must be completed first.

Run: /tdd-refactor
```

## Step 2: Mark Task In Progress

```
TaskUpdate: VERIFY → in_progress
```

## Step 3: Run 6-Phase Verification

### Phase 1: Lint

```bash
echo "=== Phase 1: Lint ===" && ruff check . 2>&1 | head -20
```

### Phase 2: Format

```bash
echo "=== Phase 2: Format ===" && ruff format --check . 2>&1 | head -10
```

### Phase 3: Tests + Coverage

```bash
echo "=== Phase 3: Tests ===" && pytest --cov=src --cov-report=term-missing --cov-fail-under=80 -q 2>&1 | tail -25
```

### Phase 4: Security

```bash
echo "=== Phase 4: Security ===" && \
grep -rn "sk-\|api_key\|password\s*=" src/ tests/ 2>/dev/null | head -5 || echo "No secrets found" && \
grep -rn "print(\|breakpoint()" src/ 2>/dev/null | head -5 || echo "No debug statements"
```

### Phase 5: Diff Review

```bash
echo "=== Phase 5: Diff ===" && git diff --stat 2>/dev/null | tail -10
```

### Phase 6: Requirements Coverage

Check that all acceptance criteria are covered by tests:
```
Read: Requirements specification from ANALYSIS phase
Verify: Each AC-XXX has corresponding test
```

## Step 4: Generate Report

```
VERIFICATION REPORT
═══════════════════════════════════════════
 Lint:       [OK/ERROR]
 Format:     [OK/ERROR]
 Tests:      [OK/ERROR] X passed
 Coverage:   XX% (min: 80%)
 Security:   [OK/ERROR]
 AC Coverage: X/Y acceptance criteria
═══════════════════════════════════════════
 Status: READY / NEEDS FIXES
═══════════════════════════════════════════
```

## Step 5: Archive to Memory Bank (if passed)

If all checks pass:

1. **Update feature-completed.json:**
```json
{
  "id": "feat-XXX",
  "name": "<feature>",
  "status": "completed",
  "completion_date": "<today>",
  "requirements_ref": "requirements/feat-XXX.json",
  "final_coverage": XX,
  "test_files": ["tests/test_<feature>.py"],
  "impl_files": ["src/<feature>.py"]
}
```

2. **Extract decisions to decisions.json** (if any new decisions made)

3. **Extract reusable patterns to test-patterns.json**

## Step 6: Mark Task Completed

```
TaskUpdate: VERIFY → completed
Metadata: {
  coverage: XX,
  allChecksPass: true,
  archivedToMemory: true
}
```

## Output

```
VERIFY Phase Complete

All checks PASSED
Coverage: XX%
Archived to Memory Bank

TDD Pipeline COMPLETE for: <feature>

Ready to commit. Use: git add . && git commit
```

If issues found, list what needs to be fixed before commit.
