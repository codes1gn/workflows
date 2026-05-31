<div align="center">

# &#x1F9F5; workflows

### Multi-Agent Workflow Orchestration for Cursor and GitHub Copilot

[![Tests](https://img.shields.io/github/actions/workflow/status/codes1gn/workflows/tests.yml?label=tests&style=flat-square)](https://github.com/codes1gn/workflows/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Cursor%20%7C%20Copilot-blueviolet?style=flat-square)](https://github.com/codes1gn/workflows)

[&#x1F310; Website](https://codes1gn.github.io/workflows) &bull;
[&#x2753; Why](#what-is-this) &bull;
[&#x1F680; Quick Start](#quick-start) &bull;
[&#x1F4CB; Built-in Workflows](#built-in-workflows) &bull;
[&#x1F527; Create Your Own](#workflow-yaml-schema) &bull;
[&#x1F9EA; Tests](#running-tests)

</div>

---

## What Is This?

**Claude Code has workflows** — scripts that orchestrate up to 16 parallel agents per run. Built-in workflows like `/deep-research` fan out across the web, cross-check findings adversarially, and return a cited report — all from one command.

**This project brings that power to Cursor and GitHub Copilot**, with:

- &#x1F4CB; **5 built-in workflow YAML definitions** (`deep-research`, `code-review`, `bug-sweep`, `plan`, `migration`)
- &#x1F916; **4 built-in sub-agent definitions** (`explore`, `plan`, `review`, `general`)
- &#x1F4DA; **5 built-in skill files** (`/deep-research`, `/code-review`, `/debug`, `/batch`, `/bug-sweep`)
- &#x1F6E0; **`wf` CLI harness** — run workflows from the terminal with real parallel execution
- &#x1F50C; **Platform adapters** for Copilot and Cursor path conventions
- &#x1F9EA; **8,400-check test suite** — 15 scenarios, 8 workers, 100% pass rate

---

## Quick Start

```bash
git clone https://github.com/codes1gn/workflows
cd workflows
pip install -e .

# Fan-out research (equivalent to Claude Code's /deep-research)
wf run deep-research "transformer architecture advancements 2024"

# Parallel 5-specialist code review
wf run code-review --var path=. "review auth module"

# Whole-codebase bug sweep
wf run bug-sweep --var path=src/

# Multi-angle planning
wf run plan "migrate our Django 3 app to Django 5"
```

---

## Built-in Workflows

| Workflow | Phases | Max Parallel | Description |
|----------|--------|:------------:|-------------|
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

## `wf` CLI Reference

```
wf run <workflow> [query] [--var K=V] [--dry-run] [-v]   Execute a workflow
wf list                                                    List all workflows
wf status                                                  Show last run status
wf create <name> [description]                            Scaffold new workflow
```

---

## Workflow YAML Schema

Define any workflow in YAML:

```yaml
name: my-workflow
description: What it does
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
      Do the second thing.
```

---

## Install Skills

```bash
# GitHub Copilot (VS Code)
cp -r builtin-skills/* ~/.copilot/skills/
cp SKILL.md ~/.copilot/skills/workflows/

# Cursor IDE
cp -r builtin-skills/* ~/.cursor/skills/
cp SKILL.md ~/.cursor/skills/workflows/
```

---

## Platform Compatibility

| Feature | GitHub Copilot | Cursor IDE | Claude Code |
|---------|:--------------:|:----------:|:-----------:|
| Run workflows via CLI | ✅ `wf run` | ✅ `wf run` | `/workflow-name` |
| Parallel agents | ✅ ThreadPoolExecutor | ✅ ThreadPoolExecutor | Native |
| Sub-agent definitions | ✅ `.github/copilot/agents/` | ✅ `.cursor/agents/` | `.claude/agents/` |
| Max parallel agents | 16 | 16 | 16 |
| Max total agents | 1,000 | 1,000 | 1,000 |
| Resumable runs | ✅ JSON state files | ✅ JSON state files | Native |

---

## Running Tests

```bash
python tests/run_tests.py --workers 8 --runs 10
```

```
15 scenarios × 7 checks × 8 workers × 10 runs = 8,400 checks
Pass rate: 100.0% ✅
```

---

## LLM Backend

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # claude-3-5-haiku (fast)
export OPENAI_API_KEY=sk-...           # gpt-4o-mini (fallback)
# Without an API key: simulation mode (useful for CI)
```

---

## License

MIT © 2025 [codes1gn](https://github.com/codes1gn)

---

<div align="center">
  <sub>8,400/8,400 checks passing &bull; Claude Code workflows for Cursor + Copilot &bull; up to 16 parallel agents</sub>
</div>
