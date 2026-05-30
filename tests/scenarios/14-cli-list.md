# Scenario 14: cli-list

`wf list`, `wf status`, and `wf create` commands are implemented.

## Commands

### wf list
Lists all available workflows from all search paths (project + user + builtin).
Calls `WorkflowRunner.list_all()`.

### wf status
Shows the most recent run's phases, agent counts, and timing.
Calls `RunState.load_latest()` + `state.print_status()`.

### wf create
Scaffolds a new workflow YAML in the user's workflow directory.
Calls `WorkflowRunner.scaffold(name, description)`.

## Runner Methods Required

- `list_all()` → list of `{name, description, path}`
- `scaffold(name, description)` → write template YAML

## State Methods Required

- `print_status()` → formatted table
- `save()` → write JSON run file
