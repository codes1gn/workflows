# Scenario 05: code-review

`code-review.yaml` implements a 3-phase parallel specialist review workflow.

## Phases

| Phase | Agents | Parallel | Description |
|-------|--------|----------|-------------|
| index | 1 | false | Map files, language, patterns |
| review | 5 | true | Parallel specialist agents |
| triage | 1 | false | Deduplicate, rank, final report |

## Specialist Agents (indices 0–4)

- 0: Security (OWASP Top 10, auth flaws, secrets)
- 1: Performance (N+1, memory leaks, complexity)
- 2: Correctness (logic errors, null handling, races)
- 3: Maintainability (naming, dead code, complexity)
- 4: Test coverage (missing tests, edge cases)
