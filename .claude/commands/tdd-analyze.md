---
description: ANALYSIS phase - define requirements before writing tests
argument-hint: <feature description>
---

# ANALYSIS Phase: $ARGUMENTS

## Step 1: Check Task Status

```
TaskList: Find ANALYSIS task for this feature
- If ANALYSIS task exists and is pending → proceed
- If ANALYSIS task is completed → skip to RED phase
- If no pipeline exists → tell user to run /tdd first
```

## Step 2: Mark Task In Progress

```
TaskUpdate: ANALYSIS → in_progress
```

## Step 3: Check Memory Bank

Read and analyze:
- `.claude/memory/feature-completed.json` → similar completed features
- `.claude/memory/decisions.json` → relevant design decisions
- `.claude/memory/test-patterns.json` → patterns to use
- `.claude/memory/feature-backlog.json` → if feature is in backlog

Report findings:
```
Memory Bank Analysis:
- Related features: [list similar features]
- Applicable decisions: [dec-001, dec-002...]
- Recommended patterns: [pat-001, pat-003...]
```

## Step 4: Use requirements-analyst Subagent

**Use the requirements-analyst subagent** to analyze requirements for: $ARGUMENTS

The subagent will:
1. Ask clarifying questions via AskUserQuestion
2. Identify acceptance criteria (must/should/could)
3. Document edge cases and out of scope
4. Reference Memory Bank for patterns

## Step 5: Create Requirements Specification

After user approval, create requirements file:

```
Write to: .claude/memory/requirements/feat-XXX.json
Content: Requirements Specification from subagent
```

## Step 6: Mark Task Completed

```
TaskUpdate: ANALYSIS → completed
Metadata: {requirementsFile: "requirements/feat-XXX.json"}
```

## Output

```
ANALYSIS Phase Complete: $ARGUMENTS

Requirements Specification: .claude/memory/requirements/feat-XXX.json

Summary:
- User Story: As a [role], I want [action]...
- Acceptance Criteria: X must, Y should, Z could
- Edge Cases: N documented
- Dependencies: [list]

Ready for RED phase: /tdd-red
```

## Enforcement

If user tries to skip to RED without completing ANALYSIS:
```
BLOCKED: ANALYSIS phase not completed

The RED phase is blocked until ANALYSIS is done.
This ensures tests cover all acceptance criteria.

Run: /tdd-analyze $ARGUMENTS
```
