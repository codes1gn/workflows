# Scenario 09: subagent-explore

`builtin-subagents/explore.md` defines the Explore sub-agent — fast, read-only codebase mapping.

## Required Frontmatter

```yaml
name: explore
description: Fast, read-only research agent
model: claude-3-5-haiku-20241022
tools: [read_file, grep, glob, list_directory]
permissions:
  allow_write: false
  allow_execute: false
```

## Behaviour Rules

- Read-only: never write, edit, or execute
- Fast: prefers grep/glob over full file reads
- Structured: always returns JSON unless explicitly asked for prose
- `allow_write: false` must be explicitly stated

## Matches Claude Code

Claude Code's built-in `Explore` agent is also read-only and uses Haiku for speed.
