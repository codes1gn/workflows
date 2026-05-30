# /bug-sweep — Workflow Skill

Systematic whole-codebase bug sweep — partition, parallel scan, reproduce, report. Designed to find bugs that tests miss and code review overlooks.

## Invocation

```
/bug-sweep [path]
```

Examples:
```
/bug-sweep .
/bug-sweep src/
/bug-sweep  # current directory
```

## What It Does

4-phase parallel bug hunting:

| Phase | Agents | Mode | Description |
|-------|--------|------|-------------|
| discover | 1 | sequential | Partition files, identify tech stack |
| scan | 6 | parallel | Parallel bug hunting across partitions |
| reproduce | 4 | parallel | Confirm bugs, assess blast radius |
| report | 1 | sequential | Actionable bug report with roadmap |

## Bug Categories

| Category | Examples |
|----------|---------|
| Null/undefined access | Dereferencing None before check |
| Resource leaks | File handles, DB connections, threads |
| Error handling | Swallowed exceptions, wrong error types |
| Type errors | Implicit coercions, wrong argument types |
| Concurrency | Race conditions, missing locks |
| API misuse | Deprecated methods, wrong signatures |
| Logic errors | Off-by-one, incorrect conditions |

## CLI Usage

```bash
wf run bug-sweep --var path=. "sweep the codebase"
wf run bug-sweep --dry-run --var path=src/ "preview"
```

## Agent Rules

1. **Partition-based scanning**: each scan agent handles a different subset of files
2. **No false positives**: only report issues you are confident are bugs
3. **Confirm before reporting**: if unsure, flag as `suspected` rather than `confirmed`
4. **Blast radius matters**: estimate how many features are affected
5. **Fix suggestions required**: every confirmed bug needs a suggested fix

## Output Format

```json
{
  "summary": {
    "total_bugs": N,
    "critical": N,
    "high": N,
    "medium_low": N
  },
  "critical_bugs": [
    {
      "file": "...",
      "line": N,
      "bug": "...",
      "severity": "critical",
      "suggested_fix": "..."
    }
  ],
  "regression_test_plan": "..."
}
```

## Severity Definitions

| Severity | Meaning |
|----------|---------|
| critical | Data loss, security breach, or crash in production |
| high | Wrong results, silent failures, degraded reliability |
| medium | Edge case failures, minor data issues |
| low | Cosmetic issues, rare edge cases |
