# Scenario 01: workflow-yaml-schema

Verifies that all YAML workflow definition files have the required top-level schema fields.

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Kebab-case workflow identifier |
| `description` | string | One-line human description |
| `version` | string | SemVer version (e.g. `1.0.0`) |
| `max_parallel_agents` | integer | Max concurrent agents (≤16) |
| `max_total_agents` | integer | Max agents per run (≤1000) |
| `phases` | list | Ordered list of workflow phases |

## Checks

1. `deep-research.yaml` has all required fields
2. `code-review.yaml` has all required fields
3. `bug-sweep.yaml` has all required fields
4. `plan.yaml` has all required fields
5. `migration.yaml` has all required fields
6. SKILL.md lists all 5 built-in workflows
7. Schema count ≥ 6 checks

## Pass Criteria

All 5 workflow YAML files parse without error and contain every required field.
