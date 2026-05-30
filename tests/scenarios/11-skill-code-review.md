# Scenario 11: skill-code-review

`builtin-skills/code-review/SKILL.md` teaches AI assistants how to run the code-review workflow.

## Required Content

- `/code-review` invocation syntax documented
- All 3 phases described (index, review, triage)
- Severity levels explained (critical/high/medium/low)
- `wf run` CLI usage shown
- Security specialist mentioned

## Usage Pattern

```
/code-review .               # review current directory
/code-review src/auth/       # review specific path
```

The skill file ensures any AI assistant (Copilot or Cursor) knows exactly how to invoke and interpret the workflow without reading the YAML source.
