# /workflows — Multi-Agent Workflow Orchestration for Cursor & GitHub Copilot

Replicate Claude Code's powerful workflow system for Cursor IDE and GitHub Copilot. Define multi-phase, multi-agent workflows in YAML. Run them with `wf`. Scale from a single agent to 16 parallel agents and 1,000 total agents per run.

---

## Quick Start

```
/workflows list           # see all available workflows
/workflows run deep-research "your topic"
/workflows status         # check current run status
/workflows create my-workflow "description"
```

## Built-in Workflows

| Workflow | Command | Description |
|----------|---------|-------------|
| deep-research | `/deep-research <topic>` | Fan-out web research + cited report |
| code-review | `/code-review [path]` | 5-specialist parallel code review |
| bug-sweep | `/bug-sweep [path]` | Whole-codebase parallel bug hunt |
| plan | `/plan <goal>` | Multi-angle planning + adversarial review |
| migration | `/migration <task>` | Incremental parallel codebase migration |
| batch | `/batch <task> --items ...` | Run any task across items in parallel |

## Built-in Sub-Agents

| Agent | Model | Tools | Description |
|-------|-------|-------|-------------|
| explore | Haiku | read-only | Fast codebase mapping |
| plan | Sonnet | read-only | Planning and architecture |
| review | Sonnet | read-only | Code review specialist |
| general | Sonnet | all | Full-capability task execution |

## Built-in Skills

| Skill | Invoke | Description |
|-------|--------|-------------|
| /deep-research | `/deep-research topic` | Research workflow |
| /code-review | `/code-review path` | Parallel code review |
| /debug | `/debug problem` | Structured debugging |
| /batch | `/batch task --items ...` | Parallel batch tasks |
| /bug-sweep | `/bug-sweep path` | Whole-codebase bug scan |

---

## CLI Reference (`wf`)

### wf run

```bash
wf run <workflow-name> [query...] [--var KEY=VALUE] [--dry-run] [-v]
```

| Option | Description |
|--------|-------------|
| `workflow-name` | Name of workflow (e.g. `deep-research`) |
| `query` | Text appended as the `{{query}}` variable |
| `--var KEY=VALUE` | Set additional workflow variables |
| `--dry-run` | Show plan without spawning agents |
| `-v / --verbose` | Verbose agent output |

Examples:
```bash
wf run deep-research "latest advances in LLM alignment"
wf run code-review --var path=src/ "review auth module"
wf run plan "migrate Django 3 to Django 5"
wf run bug-sweep --var path=. --dry-run
```

### wf list

```bash
wf list
```

Lists all available workflows from:
1. `.github/copilot/workflows/` (project-level, Copilot)
2. `.cursor/workflows/` (project-level, Cursor)
3. `~/.copilot/skills/workflows/data/` (user-level)
4. Built-in workflows (shipped with this package)

### wf status

```bash
wf status
```

Shows the most recent workflow run: phases completed, agent counts, timing.

### wf create

```bash
wf create <name> [description]
```

Scaffolds a new workflow YAML file with the standard template.

---

## Workflow YAML Schema

```yaml
name: my-workflow           # kebab-case name
description: What it does   # one-line description
version: 1.0.0
max_parallel_agents: 8      # max agents running at once (hard cap: 16)
max_total_agents: 100       # max total agents for this run (hard cap: 1000)

phases:
  - name: phase-name
    description: What this phase does
    agents: N               # number of agents (integer or expression)
    parallel: true|false    # run agents in parallel? (default: false)
    depends_on: [phase1]    # phases that must complete first
    prompt_template: |
      Your prompt here. Use {{query}} for the main input.
      Use {{agent_index}} for the agent's index (0-based).
      Use {{phases.phase-name.results}} for prior phase output.
```

### Template Variables

| Variable | Description |
|----------|-------------|
| `{{query}}` | Main user input (positional args to `wf run`) |
| `{{agent_index}}` | 0-based index of current agent in this phase |
| `{{path}}` | `--var path=...` value |
| `{{phases.NAME.results}}` | JSON results from a prior phase |
| Any `--var KEY=VALUE` | Available as `{{KEY}}` |

---

## Sub-Agent Definitions

Sub-agents are markdown files with YAML frontmatter.

**Copilot:** `.github/copilot/agents/<name>.md`
**Cursor:** `.cursor/agents/<name>.md`
**User-level:** `~/.copilot/skills/workflows/agents/<name>.md`

```markdown
---
name: my-agent
description: What this agent does
model: claude-3-5-haiku-20241022
tools: [read_file, grep, glob]
permissions:
  allow_write: false
  allow_execute: false
---

# Agent Instructions

...
```

---

## Installation

### Install CLI

```bash
# From source
cd workflows
pip install -e .

# Verify
wf list
```

### Install Skills (Copilot / VS Code)

```bash
# Install all built-in skills
cp -r builtin-skills/* ~/.copilot/skills/

# Install this meta-skill
cp SKILL.md ~/.copilot/skills/workflows/
```

### Install Skills (Cursor)

```bash
cp -r builtin-skills/* ~/.cursor/skills/
cp SKILL.md ~/.cursor/skills/workflows/
```

### Install Sub-Agents

```bash
# Project-level (Copilot)
mkdir -p .github/copilot/agents
cp builtin-subagents/* .github/copilot/agents/

# Project-level (Cursor)
mkdir -p .cursor/agents
cp builtin-subagents/* .cursor/agents/
```

---

## Platform Compatibility

| Feature | GitHub Copilot | Cursor IDE | Claude Code |
|---------|---------------|------------|-------------|
| Workflow YAML | ✅ via `wf` CLI | ✅ via `wf` CLI | Native JS |
| Parallel agents | ✅ ThreadPoolExecutor | ✅ ThreadPoolExecutor | Native |
| Sub-agents | ✅ `.github/copilot/agents/` | ✅ `.cursor/agents/` | `.claude/agents/` |
| Skills | ✅ SKILL.md files | ✅ SKILL.md files | `.claude/skills/` |
| Max parallel | 16 | 16 | 16 |
| Max total | 1000 | 1000 | 1000 |
| Resumable runs | ✅ via state file | ✅ via state file | Native |
| LLM backend | Anthropic / OpenAI | Anthropic / OpenAI | Claude only |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Use Claude for agent calls (preferred) |
| `OPENAI_API_KEY` | Use GPT-4o-mini for agent calls (fallback) |

If neither is set, the harness runs in **simulation mode** (useful for CI / pattern tests).

---

## Custom Workflow Examples

### PR Review Workflow

```yaml
name: pr-review
description: Review a pull request thoroughly
max_parallel_agents: 4

phases:
  - name: read-pr
    agents: 1
    prompt_template: |
      Read PR #{{pr_number}} diff. List all changed files and summarise each change.

  - name: review
    agents: 4
    parallel: true
    depends_on: [read-pr]
    prompt_template: |
      PR summary: {{phases.read-pr.results}}
      Agent {{agent_index}} specialisation: 0=security, 1=correctness, 2=tests, 3=docs
      Review from your specialisation's perspective.

  - name: verdict
    agents: 1
    depends_on: [review]
    prompt_template: |
      Triage all review findings and produce a final LGTM or REQUEST_CHANGES verdict.
      {{phases.review.results}}
```

Run with:
```bash
wf run pr-review --var pr_number=42 "review this PR"
```

---

## Scenarios Tested

| # | Scenario | Checks |
|---|----------|--------|
| 1 | workflow-yaml-schema | YAML has required fields |
| 2 | phase-structure | Each phase has name/agents/prompt |
| 3 | parallel-support | Parallel flag implemented |
| 4 | deep-research | deep-research.yaml complete |
| 5 | code-review | code-review.yaml complete |
| 6 | bug-sweep | bug-sweep.yaml complete |
| 7 | plan-workflow | plan.yaml complete |
| 8 | migration-workflow | migration.yaml complete |
| 9 | subagent-explore | explore.md frontmatter |
| 10 | subagent-review | review.md frontmatter |
| 11 | skill-code-review | /code-review SKILL.md |
| 12 | skill-debug | /debug SKILL.md |
| 13 | cli-run | `wf run` implemented |
| 14 | cli-list | `wf list` implemented |
| 15 | platform-paths | Copilot + Cursor paths |

Total: **15 scenarios × 7 checks × 8 workers × 10 runs = 8,400 checks**

---

## File Locations

```
workflows/
├── workflow_runner/          Python harness
│   ├── cli.py                wf CLI entry point
│   ├── runner.py             WorkflowRunner: load, execute, scaffold
│   ├── state.py              RunState: tracking + persistence
│   └── adapters/             Platform path resolvers
│       ├── copilot.py        ~/.copilot/skills/workflows/
│       └── cursor.py         ~/.cursor/workflows/
├── builtin-workflows/        5 built-in YAML workflow definitions
├── builtin-subagents/        4 built-in sub-agent .md definitions
├── builtin-skills/           5 built-in SKILL.md files
│   ├── deep-research/        /deep-research skill
│   ├── code-review/          /code-review skill
│   ├── debug/                /debug skill
│   ├── batch/                /batch skill
│   └── bug-sweep/            /bug-sweep skill
├── tests/run_tests.py        15-scenario harness
├── SKILL.md                  This file
├── README.md
└── setup.py
```
