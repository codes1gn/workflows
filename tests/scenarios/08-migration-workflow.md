# Scenario 08: migration-workflow

`migration.yaml` implements a 4-phase parallel codebase migration workflow.

## Phases

| Phase | Agents | Parallel | Description |
|-------|--------|----------|-------------|
| audit | 1 | false | Scope, complexity classification, breaking changes |
| migrate | 6 | true | Parallel transformation agents |
| verify | 2 | true | Correctness + consistency verification |
| report | 1 | false | Completion report with remaining manual steps |

## Use Cases

- Framework version upgrades (Django 3→5, React 17→19)
- API deprecation migrations
- Language syntax modernisation
- Dependency replacements
