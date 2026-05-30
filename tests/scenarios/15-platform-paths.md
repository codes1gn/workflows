# Scenario 15: platform-paths

Verifies that platform adapters return correct paths for Copilot and Cursor installations.

## Expected Paths

| Platform | User Workflows | Project Workflows | Skills |
|----------|---------------|------------------|--------|
| Copilot | `~/.copilot/skills/workflows/data/` | `.github/copilot/workflows/` | `~/.copilot/skills/` |
| Cursor | `~/.cursor/workflows/` | `.cursor/workflows/` | `~/.cursor/skills/` |

## Checks

1. `CopilotAdapter.workflow_dir()` uses `.copilot` path
2. `CopilotAdapter` references `.github` for project-level
3. `CopilotAdapter.instructions_file()` returns `copilot-instructions.md`
4. `CursorAdapter.workflow_dir()` uses `.cursor` path
5. `CursorAdapter.rules_dir()` references `rules`
6. SKILL.md documents `~/.copilot/skills/` install path
7. SKILL.md documents `~/.cursor/skills/` install path

## Pass Criteria

Both adapters correctly resolve to platform-standard paths.
Both paths are documented in SKILL.md installation guide.
