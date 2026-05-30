# /debug — Workflow Skill

Systematic debugging workflow — reproduce, isolate, hypothesise, verify, fix.

## Invocation

```
/debug <description of the problem>
```

Examples:
```
/debug API returns 500 on POST /users when email contains + sign
/debug test suite flaky — random failures in CI but not locally
/debug memory usage grows without bound after 1000 requests
```

## What It Does

5-step structured debugging process:

| Step | Description |
|------|-------------|
| 1. Reproduce | Confirm the bug is reproducible; write a minimal repro |
| 2. Isolate | Narrow down to the smallest failing unit |
| 3. Hypothesise | Generate 3+ root cause hypotheses, ranked by likelihood |
| 4. Verify | Test each hypothesis, starting from most likely |
| 5. Fix | Apply fix, verify it resolves the bug, write regression test |

## Agent Rules

**When debugging:**

1. **Never assume the obvious cause** — always generate ≥3 hypotheses first
2. **Minimal reproduction first** — before fixing, write the smallest test that shows the bug
3. **Read the stack trace completely** — the actual cause is often 3-5 frames deep
4. **Check recent changes** — `git log --oneline -20` before digging into code
5. **Verify the fix** — run the original failing case after the fix; do not just "eyeball" it
6. **Write a regression test** — every fix needs a test to prevent recurrence

## Debugging Checklist

```
□ Can I reproduce the bug reliably?
□ Is it environment-specific (OS, Python version, env vars)?
□ When did it start? (git bisect if needed)
□ What does the stack trace say exactly?
□ What are the inputs that trigger it?
□ Have I read the relevant library docs / source?
□ Is the fix minimal and targeted?
□ Is there a regression test?
```

## Common Root Causes by Symptom

| Symptom | Common Causes |
|---------|--------------|
| 500 error | Unhandled exception, missing null check, DB constraint violation |
| Flaky test | Race condition, time dependency, shared mutable state |
| Memory leak | Circular refs, event listeners not removed, cache without eviction |
| Slow response | N+1 query, missing index, synchronous I/O in async context |
| Import error | Circular import, missing __init__.py, virtual env not activated |

## Output Format

After debugging, report:

```json
{
  "bug": "concise description",
  "root_cause": "exact root cause found",
  "fix": "what was changed",
  "files_changed": ["..."],
  "regression_test": "test name / command to verify",
  "confidence": "high | medium | low"
}
```
