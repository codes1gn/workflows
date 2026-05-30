# Scenario 02: phase-structure

Each workflow phase must have `name`, `agents`, `parallel`, and `prompt_template`.

## Required Phase Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ | Unique phase identifier |
| `agents` | ✅ | Number of agents to spawn |
| `parallel` | ✅ | Whether agents run concurrently |
| `prompt_template` | ✅ | Template with `{{variable}}` substitution |
| `description` | optional | Human-readable description |
| `depends_on` | optional | Prior phases that must complete |

## Checks

Tests deep-research, code-review, and plan workflows for all 4 required fields.
