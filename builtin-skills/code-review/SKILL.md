# /code-review — Workflow Skill

Run a comprehensive parallel multi-angle code review across an entire codebase or PR diff. Five specialist review agents run in parallel, then a lead agent triages all findings.

## Invocation

```
/code-review [path]
```

Examples:
```
/code-review .
/code-review src/auth/
/code-review  # defaults to current directory
```

## What It Does

Executes a 3-phase workflow:

| Phase | Agents | Mode | Description |
|-------|--------|------|-------------|
| index | 1 | sequential | Map files, identify language + patterns |
| review | 5 | parallel | Specialist agents (security/perf/correctness/style/tests) |
| triage | 1 | sequential | Deduplicate, rank, and produce final report |

## Specialist Agents

| Index | Specialisation |
|-------|---------------|
| 0 | Security (injection, auth flaws, secrets, OWASP Top 10) |
| 1 | Performance (N+1, memory leaks, algorithmic complexity) |
| 2 | Correctness (logic errors, null handling, race conditions) |
| 3 | Maintainability (naming, dead code, cyclomatic complexity) |
| 4 | Test coverage (missing tests, edge cases, flaky patterns) |

## CLI Usage

```bash
wf run code-review --var path=. "review the codebase"
wf run code-review --dry-run --var path=src/
```

## Issue Severity

| Severity | Meaning | Action |
|----------|---------|--------|
| critical | Must fix before merge | Block PR |
| high | Fix this sprint | Assign issue |
| medium | Backlog | Track as tech debt |
| low | Optional improvement | Consider |

## Output Format

```json
{
  "summary": "...",
  "critical": [{"file": "...", "line": N, "issue": "...", "fix": "..."}],
  "high": [...],
  "medium": [...],
  "low": [...],
  "positives": [...]
}
```

## Agent Rules

1. **Each specialist agent reviews the ENTIRE codebase** — do not partition files between agents
2. **Specialisations are non-overlapping** — security agent does NOT comment on style
3. **Every issue must have a fix** — never report a problem without a suggested solution
4. **Triage deduplication**: if two agents flag the same issue, merge into one
5. **Positives matter**: note what is done well (encourages good patterns)
