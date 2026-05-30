# Scenario 13: cli-run

`wf run` is fully implemented in `cli.py` and `workflow_runner/runner.py`.

## CLI Args

| Arg | Type | Description |
|-----|------|-------------|
| `workflow_name` | positional | Name of workflow to run |
| `query` | nargs=* | Main input appended as `{{query}}` |
| `--var KEY=VALUE` | append | Extra template variables |
| `--dry-run` | flag | Show plan without agents |
| `-v / --verbose` | flag | Verbose agent output |

## Runner Requirements

- `execute(workflow, variables, state, dry_run, verbose)` method
- `load(name)` method — search all workflow dirs
- `dry_run` mode shows phase plan without spawning agents
