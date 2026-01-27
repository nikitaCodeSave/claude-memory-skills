---
description: RED phase - write failing tests for feature
argument-hint: <feature description>
---

# RED Phase: $ARGUMENTS

## Step 1: Check Task Dependencies

```
TaskList: Find RED task for this feature pipeline
Check: Is blockedBy empty? (ANALYSIS must be completed)
```

**If ANALYSIS not completed:**
```
BLOCKED: RED phase cannot start

The ANALYSIS phase must be completed first.
This ensures tests cover all acceptance criteria.

Run: /tdd-analyze $ARGUMENTS
```

## Step 2: Mark Task In Progress

```
TaskUpdate: RED → in_progress
```

## Step 3: Load Requirements Specification

```
Read: .claude/memory/requirements/<feature>.json
Extract:
- Acceptance Criteria (AC-001, AC-002...)
- Edge Cases
- Technical Constraints
```

## Step 4: Use tdd-test-writer Subagent

**Use the tdd-test-writer subagent** to write failing tests:

**Feature:** $ARGUMENTS

**Requirements from ANALYSIS phase:**
- [Pass acceptance criteria and edge cases from requirements spec]
- [Pass applicable test patterns from test-patterns.json]
- [Pass relevant decisions from decisions.json]

**Subagent must:**
1. Read test patterns from Memory Bank
2. Write tests covering ALL acceptance criteria
3. Add traceability comments: `# AC-001: description`
4. Run tests and confirm they FAIL
5. Report test file path and failure count

## Step 5: Verify Tests Fail

```bash
pytest tests/test_<feature>.py -v --tb=short
```

Expected: All tests FAIL (no implementation yet)

## Step 6: Mark Task Completed

```
TaskUpdate: RED → completed
Metadata: {
  testFile: "tests/test_<feature>.py",
  testCount: N,
  acceptanceCriteriaCovered: ["AC-001", "AC-002"...]
}
```

## Output

```
RED Phase Complete: $ARGUMENTS

Test file: tests/test_<feature>.py
Tests written: N
Acceptance Criteria covered: AC-001, AC-002, AC-003

Tests FAIL as expected:
- test_<name>: <error type>
- test_<name>: <error type>

Ready for GREEN phase: /tdd-green
```

## Traceability

Each test should trace to acceptance criteria:

```python
class TestFeature:
    """Tests for feature (feat-XXX)"""

    # AC-001: Valid input passes
    def test_valid_input_passes(self):
        """AC-001: valid input should pass"""
        ...

    # AC-002: Invalid input raises error
    def test_invalid_input_raises(self):
        """AC-002: invalid input raises ValidationError"""
        ...
```
