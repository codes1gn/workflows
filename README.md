# workflows

> **Multi-agent workflow orchestration for Cursor and GitHub Copilot** — the Claude Code `/workflows` experience, reimagined for every AI coding assistant.

[![Tests](https://github.com/codes1gn/workflows/actions/workflows/tests.yml/badge.svg)](https://github.com/codes1gn/workflows/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Cursor%20%7C%20Copilot-blueviolet)](https://github.com/codes1gn/workflows)

---

## What Is This?

**Claude Code has workflows** — JavaScript scripts that orchestrate up to **16 parallel agents** and **1,000 total agents** per run. Built-in workflows like `/deep-research` fan out across the web, cross-check findings adversarially, and return a comprehensive cited report — all from one command.

**This project brings that power to Cursor and GitHub Copilot**, with:

- 📋 **5 built-in workflow YAML definitions** (`deep-research`, `code-review`, `bug-sweep`, `plan`, `migration`)
- 🤖 **4 built-in sub-agent definitions** (`explore`, `plan`, `review`, `general`)
- 📚 **5 built-in skill files** (`/deep-research`, `/code-review`, `/debug`, `/batch`, `/bug-sweep`)
- 🛠️ **`wf` CLI harness** — run workflows from the terminal with real parallel agent execution
- 🔌 **Platform adapters** for Copilot and Cursor path conventions
- 🧪 **8,400-check test suite** — 15 scenarios, 8 workers, 100% pass rate

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/codes1gn/workflows
cd workflows
pip install -e .
```

### 2. Run a Workflow

```bash
# Fan-out research (equivalent to Claude Code's /deep-research)
wf run deep-research "transformer architecture advancements 2024"

# Parallel 5-specialist code review
wf run code-review --var path=. "review auth module"

# Whole-codebase bug sweep
wf run bug-sweep --var path=src/

# Multi-angle planning
wf run plan "migrate our Django 3 app to Django 5"
```

### 3. List Available Workflows

```bash
wf list
```

### 4. Dry Run (see the plan first)

```bash
wf run deep-research --dry-run "your topic"
```

---

## Built-in Workflows

| Workflow | Phases | Max Parallel | Description |
|----------|--------|-------------|-------------|
| `deep-research` | decompose → search → cross-check → synthesize | 8 | Fan-out research + cited report |
| `code-review` | index → review (5 specialists) → triage | 6 | Security, perf, correctness, style, tests |
| `bug-sweep` | discover → scan → reproduce → report | 8 | Whole-codebase parallel bug hunt |
| `plan` | understand → explore → challenge → synthesize | 4 | Multi-angle plan + adversarial review |
| `migration` | audit → migrate → verify → report | 8 | Incremental parallel codebase migration |

---

## Built-in Sub-Agents

| Agent | Model | Permissions | Description |
|-------|-------|-------------|-------------|
| `explore` | Haiku | read-only | Fast codebase mapping, grep/glob specialist |
| `plan` | Sonnet | read-only | Planning and architecture, JSON output |
| `review` | Sonnet | read-only | 5-dimension code reviewer |
| `general` | Sonnet | read + write + exec | Full-capability task executor |

---

## Built-in Skills

Install and invoke from your AI assistant:

| Skill | Command | Description |
|-------|---------|-------------|
| deep-research | `/deep-research <topic>` | 4-phase fan-out research |
| code-review | `/code-review [path]` | Parallel specialist review |
| debug | `/debug <problem>` | 5-step structured debugging |
| batch | `/batch <task> --items ...` | Parallel batch tasks |
| bug-sweep | `/bug-sweep [path]` | Whole-codebase bug hunt |

---

## `wf` CLI Reference

```
wf run <workflow>  [query] [--var K=V] [--dry-run] [-v]    Execute a workflow
wf list                                                       List all workflows
wf status                                                     Show last run status
wf create <name> [description]                               Scaffold new workflow
```

### Examples

```bash
# Research a topic (fan-out, parallel, cited report)
wf run deep-research "state of the art in LLM alignment 2025"

# Review a PR's changed files
wf run code-review --var path=. "review src/auth/"

# Sweep for bugs across entire repo
wf run bug-sweep --var path=.

# Plan a large refactor
wf run plan "extract billing module into its own microservice"

# Run your own custom workflow
wf create my-workflow "Does something great"
wf run my-workflow "input data"
```

---

## Workflow YAML Schema

Define any workflow in YAML:

```yaml
name: my-workflow
description: What it does
version: 1.0.0
max_parallel_agents: 8   # hard cap: 16
max_total_agents: 100    # hard cap: 1000

phases:
  - name: phase-one
    agents: 1
    parallel: false
    prompt_template: |
      Query: {{query}}
      Do the first thing.

  - name: phase-two
    agents: 4
    parallel: true
    depends_on: [phase-one]
    prompt_template: |
      Prior results: {{phases.phase-one.results}}
      Agent index: {{agent_index}}
      Do the second thing for this agent's slice.
```

### Template Variables

| Variable | Value |
|----------|-------|
| `{{query}}` | Positional args from `wf run` |
| `{{agent_index}}` | 0-based agent index in current phase |
| `{{path}}` | `--var path=...` value |
| `{{phases.NAME.results}}` | JSON from a prior phase |
| `{{ANY_VAR}}` | Any `--var KEY=VALUE` |

---

## Installation Guide

### Install Skills (GitHub Copilot)

```bash
# Install built-in skills
cp -r builtin-skills/* ~/.copilot/skills/

# Install meta-skill
mkdir -p ~/.copilot/skills/workflows
cp SKILL.md ~/.copilot/skills/workflows/
```

### Install Skills (Cursor IDE)

```bash
cp -r builtin-skills/* ~/.cursor/skills/
mkdir -p ~/.cursor/skills/workflows
cp SKILL.md ~/.cursor/skills/workflows/
```

### Install Sub-Agents (project-level)

```bash
# Copilot (VS Code)
mkdir -p .github/copilot/agents
cp builtin-subagents/* .github/copilot/agents/

# Cursor
mkdir -p .cursor/agents
cp builtin-subagents/* .cursor/agents/
```

### Install Workflows (project-level)

```bash
# Copilot
mkdir -p .github/copilot/workflows
cp builtin-workflows/*.yaml .github/copilot/workflows/

# Cursor
mkdir -p .cursor/workflows
cp builtin-workflows/*.yaml .cursor/workflows/
```

---

## Platform Compatibility

| Feature | GitHub Copilot | Cursor IDE | Claude Code |
|---------|:---:|:---:|:---:|
| Run workflows via CLI | ✅ `wf run` | ✅ `wf run` | `/workflow-name` |
| Parallel agents | ✅ ThreadPoolExecutor | ✅ ThreadPoolExecutor | Native |
| Sub-agent definitions | ✅ `.github/copilot/agents/` | ✅ `.cursor/agents/` | `.claude/agents/` |
| Skill files | ✅ SKILL.md | ✅ SKILL.md | `.claude/skills/` |
| Max parallel agents | 16 | 16 | 16 |
| Max total agents | 1,000 | 1,000 | 1,000 |
| Resumable runs | ✅ JSON state files | ✅ JSON state files | Native |
| LLM backend | Anthropic / OpenAI | Anthropic / OpenAI | Claude only |

---

## LLM Backend

Set an API key to run real agents:

```bash
# Anthropic (preferred — uses claude-3-5-haiku for speed)
export ANTHROPIC_API_KEY=sk-ant-...

# OpenAI (fallback — uses gpt-4o-mini)
export OPENAI_API_KEY=sk-...
```

Without an API key, the harness runs in **simulation mode** — useful for CI, dry runs, and testing.

---

## Running Tests

```bash
python tests/run_tests.py
```

**Expected output:**

```
  RESULT: PASS ✅
  Total checks : 8,400
  Failures     : 0
  Pass rate    : 100.0%
```

Test math: **15 scenarios × 7 checks × 8 workers × 10 runs = 8,400 checks**

---

## Project Structure

```
workflows/
├── workflow_runner/              Python harness (wf CLI)
│   ├── cli.py                    run / list / status / create commands
│   ├── runner.py                 WorkflowRunner: load, execute phases, parallel agents
│   ├── state.py                  RunState: track + persist run results
│   └── adapters/
│       ├── copilot.py            ~/.copilot/skills/workflows/ paths
│       └── cursor.py             ~/.cursor/workflows/ paths
├── builtin-workflows/            5 YAML workflow definitions
│   ├── deep-research.yaml        4-phase fan-out research
│   ├── code-review.yaml          5-specialist parallel review
│   ├── bug-sweep.yaml            4-phase parallel bug hunt
│   ├── plan.yaml                 4-phase adversarial planning
│   └── migration.yaml            4-phase incremental migration
├── builtin-subagents/            4 sub-agent .md definitions
│   ├── explore.md                Haiku, read-only, fast mapping
│   ├── plan.md                   Sonnet, read-only, planning
│   ├── review.md                 Sonnet, read-only, code review
│   └── general.md                Sonnet, all tools, full capability
├── builtin-skills/               5 SKILL.md files
│   ├── deep-research/SKILL.md
│   ├── code-review/SKILL.md
│   ├── debug/SKILL.md
│   ├── batch/SKILL.md
│   └── bug-sweep/SKILL.md
├── tests/
│   ├── run_tests.py              8,400-check harness
│   └── scenarios/               15 scenario docs
├── SKILL.md                      Meta-skill: /workflows command reference
├── README.md
├── setup.py
└── requirements.txt
```

---

## Inspired By

- **[Claude Code Workflows](https://docs.anthropic.com/en/docs/claude-code/workflows)** — the original multi-agent orchestration system
- **[Agentskills.io](https://agentskills.io)** — open SKILL.md standard
- **[codes1gn/agent-handoff](https://github.com/codes1gn/agent-handoff)** — cross-session memory for AI agents
- **[codes1gn/incubate](https://github.com/codes1gn/incubate)** — autonomous project incubation pipeline

---

## License

MIT © 2025 codes1gn
