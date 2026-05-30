# Architecture: workflows

## 1. System Overview

```
User / AI Agent
       │
       ▼
  wf CLI (cli.py)
       │
       ▼
  WorkflowRunner (runner.py)
  ├── load(name) → parse YAML
  ├── execute(workflow, vars, state)
  │   ├── for each phase in workflow.phases:
  │   │   ├── sequential: run agents one by one
  │   │   └── parallel:   ThreadPoolExecutor(max_workers=max_parallel)
  │   │       └── _call_agent(prompt, phase, idx)
  │   │           ├── ANTHROPIC_API_KEY → Anthropic SDK → claude-3-5-haiku
  │   │           ├── OPENAI_API_KEY → OpenAI SDK → gpt-4o-mini
  │   │           └── (neither) → simulation mode
  │   └── state.save() → JSON run file
  └── list_all() / scaffold(name)

  Platform Adapters
  ├── CopilotAdapter → ~/.copilot/skills/workflows/data/
  └── CursorAdapter  → ~/.cursor/workflows/

  RunState (state.py)
  └── ~/.copilot/skills/workflows/data/runs/<run-id>-<name>.json
```

## 2. Component Design

### workflow_runner/cli.py — CLI Entry Point

**Responsibility**: Parse CLI arguments, dispatch to runner commands.

**Commands**:
- `wf run` → `cmd_run` → `WorkflowRunner.execute()`
- `wf list` → `cmd_list` → `WorkflowRunner.list_all()`
- `wf status` → `cmd_status` → `RunState.load_latest()`
- `wf create` → `cmd_create` → `WorkflowRunner.scaffold()`

### workflow_runner/runner.py — WorkflowRunner

**Responsibility**: Load YAML definitions, execute phases, spawn agents.

**Key Methods**:
- `load(name)` — search adapter dirs + builtin dir for `<name>.yaml`, parse with PyYAML
- `list_all()` — enumerate all .yaml files from all dirs, return name+description
- `execute(workflow, variables, state, dry_run, verbose)` — phase-by-phase execution engine
- `scaffold(name, description)` — write template YAML to user's workflow dir
- `_call_agent(prompt, phase, idx, verbose)` — LLM call with fallback chain

**Execution Model**:
```
Phase loop (sequential):
  if parallel AND agents > 1:
    ThreadPoolExecutor(max_workers=min(agents, max_parallel))
    → submit run_agent(i) for each i
    → as_completed() collect results
  else:
    sequential loop run_agent(i)
  
  variables["phases.NAME.results"] = JSON(results)
  state.complete_phase(name, results)
```

**Hard Caps** (immutable):
```python
MAX_PARALLEL = 16    # matches Claude Code
MAX_TOTAL = 1000     # matches Claude Code
```

### workflow_runner/state.py — RunState

**Responsibility**: Track and persist workflow run state.

**State Structure**:
```json
{
  "run_id": "20250601-120000",
  "workflow": "deep-research",
  "status": "done",
  "started_at": "ISO-8601",
  "finished_at": "ISO-8601",
  "phases": {
    "decompose": {"status": "done", "results": [...]},
    "search": {"status": "done", "results": [...]}
  }
}
```

**Persistence**: `~/.copilot/skills/workflows/data/runs/<run-id>-<name>.json`

### workflow_runner/adapters/ — Platform Adapters

**Responsibility**: Resolve platform-specific paths without hardcoding.

**Resolution Priority**:
1. Project-level (`.github/copilot/workflows/` or `.cursor/workflows/`) — if exists
2. User-level (`~/.copilot/skills/workflows/data/` or `~/.cursor/workflows/`) — fallback

## 3. Workflow YAML Format

```yaml
name: workflow-name           # required: kebab-case identifier
description: Human description # required: one-line
version: 1.0.0                # required: SemVer
max_parallel_agents: 8        # optional: default 4, cap 16
max_total_agents: 100         # optional: default 50, cap 1000

phases:
  - name: phase-name          # required: unique within workflow
    description: optional     # optional: human description
    agents: N                 # required: integer ≥ 1
    parallel: true|false      # optional: default false
    depends_on: [phase-a]     # optional: phase dependencies (enforced by order)
    prompt_template: |        # required: Jinja-like {{variable}} substitution
      prompt text here
```

### Template Variable Resolution

| Variable | Source |
|----------|--------|
| `{{query}}` | Positional args to `wf run` |
| `{{agent_index}}` | 0-based agent index in current phase |
| `{{path}}` | `--var path=...` |
| `{{phases.NAME.results}}` | JSON-serialized results from named prior phase |
| `{{KEY}}` | Any `--var KEY=VALUE` flag |

Implemented via simple regex: `re.sub(r"\{\{([^}]+)\}\}", _sub, template)`

## 4. Sub-Agent Definition Format

```markdown
---
name: agent-name
description: What this agent does
model: claude-3-5-haiku-20241022 | claude-3-5-sonnet-20241022
tools: [read_file, grep, glob, write_file, bash]
permissions:
  allow_write: false
  allow_execute: false
  max_tool_calls: 200
---

# Agent Name

Instructions for the agent...
```

**Paths**:
- Copilot: `.github/copilot/agents/<name>.md` (project) or `~/.copilot/skills/workflows/agents/` (user)
- Cursor: `.cursor/agents/<name>.md` (project) or `~/.cursor/agents/` (user)

## 5. Skill File Format

Following the [agentskills.io](https://agentskills.io) open standard:

```
builtin-skills/<skill-name>/SKILL.md
```

SKILL.md documents:
- Invocation syntax
- What the workflow does (phase table)
- CLI usage examples
- Manual agent instructions (no CLI fallback)
- Output format / JSON schema
- Agent rules and constraints

## 6. LLM Backend Architecture

```
_call_agent(prompt, phase, idx, verbose)
       │
       ├─ ANTHROPIC_API_KEY set?
       │      └─ Yes → _call_anthropic(prompt, key)
       │             → anthropic.Anthropic(api_key)
       │             → claude-3-5-haiku-20241022
       │             → max_tokens=4096
       │
       ├─ OPENAI_API_KEY set?
       │      └─ Yes → _call_openai(prompt, key)
       │             → openai.OpenAI(api_key)
       │             → gpt-4o-mini
       │             → max_tokens=4096
       │
       └─ Neither → simulation mode
              → sleep(0.05) for realism
              → return JSON {status: "simulated", ...}
```

**Rationale**: Haiku (Anthropic) preferred for speed and cost. GPT-4o-mini as OpenAI fallback. Simulation mode enables CI/CD without API keys.

## 7. Directory Layout

```
~/.copilot/skills/workflows/
├── data/
│   ├── *.yaml                 # user-defined workflow definitions
│   └── runs/
│       └── <run-id>.json      # run state files
└── agents/
    └── *.md                   # user-defined sub-agent definitions

~/.cursor/workflows/
└── *.yaml                     # user-defined workflow definitions (Cursor)

<project>/
├── .github/copilot/
│   ├── workflows/*.yaml       # project-level workflows (Copilot)
│   └── agents/*.md            # project-level agents (Copilot)
└── .cursor/
    ├── workflows/*.yaml       # project-level workflows (Cursor)
    └── agents/*.md            # project-level agents (Cursor)
```

## 8. Decision Log

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| Workflow format | YAML, JSON, Python DSL, JS | YAML | Readable, version-controllable, familiar |
| Parallelism | asyncio, threading, multiprocessing | ThreadPoolExecutor | Best for I/O-bound LLM calls; standard lib |
| CLI framework | click, typer, argparse | argparse | No extra dependencies |
| YAML parsing | pyyaml, ruamel.yaml, custom | pyyaml + minimal fallback | pyyaml is standard; fallback for no-dep installs |
| LLM backends | Anthropic-only, OpenAI-only, multi | Both + simulation | Maximum compatibility |
| State storage | SQLite, Redis, JSON files | JSON files | Simple, portable, no extra services |
| Max parallel | 4, 8, 16, 32 | 16 | Matches Claude Code's documented limit |
