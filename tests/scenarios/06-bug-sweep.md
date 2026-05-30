# Scenario 06: bug-sweep

`bug-sweep.yaml` implements a 4-phase parallel bug hunting workflow.

## Phases

| Phase | Agents | Parallel | Description |
|-------|--------|----------|-------------|
| discover | 1 | false | Partition files, identify tech stack |
| scan | 6 | true | Parallel bug hunters across partitions |
| reproduce | 4 | true | Confirm bugs, blast radius, test suggestions |
| report | 1 | false | Actionable bug report with severity breakdown |

## Bug Categories Covered

- Null/undefined access
- Resource leaks
- Error handling failures
- Type errors
- Concurrency bugs
- API misuse
- Business logic errors
