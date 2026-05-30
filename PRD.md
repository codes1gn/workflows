# PRD: workflows — Claude Code Workflows Equivalent for Cursor & GitHub Copilot

## 1. Problem Statement

Claude Code introduced a powerful multi-agent workflow system where developers can:
- Define JavaScript workflow scripts that orchestrate many agents in parallel
- Run built-in workflows like `/deep-research` (fan-out web research) with one command
- Scale to 16 parallel agents and 1,000 total agents per run
- Create custom workflows and save them as reusable commands

**Cursor and GitHub Copilot users have no equivalent**. When developers switch from Claude Code to Cursor or Copilot, they lose access to multi-agent orchestration, parallel execution, and the built-in workflow library.

## 2. Goals

| # | Goal | Success Criterion |
|---|------|-----------------|
| G1 | YAML workflow definitions | Developers can define multi-phase, multi-agent workflows in YAML |
| G2 | Parallel execution | Multiple agents run in parallel with configurable concurrency |
| G3 | Built-in workflows | 5+ built-in workflows matching Claude Code's repertoire |
| G4 | Sub-agent framework | Named, reusable sub-agent definitions for Cursor and Copilot |
| G5 | Skill files | Skill SKILL.md files teach AI assistants how to use each workflow |
| G6 | CLI harness | `wf` command runs any workflow with `wf run <name> <query>` |
| G7 | Platform adapters | Works identically with Copilot and Cursor path conventions |
| G8 | Extensible | Developers can create custom workflows with `wf create` |

## 3. Non-Goals

- **Not a JavaScript executor** — Python-based harness, not a JS runtime
- **Not a replacement for the AI assistant** — the harness orchestrates; the AI reasons
- **Not a SaaS platform** — purely local tooling, bring your own API key
- **Not Claude-specific** — works with Anthropic or OpenAI backends

## 4. User Stories

**US-1**: As a developer on Copilot, I want to run `/deep-research` to get a comprehensive cited report on a topic, just like Claude Code users can.

**US-2**: As a team, I want to run a parallel code review across 5 specialist agents (security, perf, correctness, style, tests) on our PR before merging.

**US-3**: As a developer, I want to define a custom `pr-review` workflow in YAML and share it with my team via version control.

**US-4**: As an agent, I want SKILL.md files that teach me exactly how to invoke each workflow, what the output format is, and how to interpret results.

**US-5**: As a developer, I want to dry-run a workflow first to see the execution plan before spending API credits.

## 5. Workflow Design Principles

### Phase-based Execution
Workflows consist of ordered phases. Each phase completes before the next begins.

### Parallel Agents Within Phase
Within a phase, agents run in parallel (up to `max_parallel_agents`). Each agent receives the same prompt template with `{{agent_index}}` for differentiation.

### Template Variables
Prompt templates use `{{variable}}` syntax. Agents can access prior phase results via `{{phases.PHASE.results}}`.

### Hard Limits
- `max_parallel_agents`: cap at 16 (matches Claude Code)
- `max_total_agents`: cap at 1,000 (matches Claude Code)

## 6. Built-in Workflows

| Workflow | Claude Code Equivalent | Key Feature |
|----------|----------------------|-------------|
| deep-research | `/deep-research` | 4-phase fan-out, cross-check, cited report |
| code-review | N/A (custom) | 5 specialists, adversarial triage |
| bug-sweep | N/A (custom) | Partition-based parallel scan |
| plan | `/plan` (proposed) | Adversarial challenge phase |
| migration | N/A (custom) | Incremental parallel migration |

## 7. Built-in Sub-Agents

| Agent | Basis | Key Constraint |
|-------|-------|----------------|
| explore | Claude Code Explore | Read-only, Haiku model |
| plan | Claude Code Plan | Read-only, Sonnet |
| review | Custom | Read-only, code-focused |
| general | Claude Code General | All tools, Sonnet |

## 8. Technical Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.9+ | Universal, consistent with other tools in the ecosystem |
| Workflow format | YAML | Readable, well-supported, familiar to developers |
| Parallelism | `concurrent.futures.ThreadPoolExecutor` | Standard library, no extra deps |
| LLM backends | Anthropic SDK + OpenAI SDK | Optional extras; simulation mode if neither |
| YAML parsing | `pyyaml` | The standard Python YAML library |
| CLI | `argparse` | Standard library, no extra deps |
| State persistence | JSON files in `~/.copilot/skills/workflows/data/runs/` | Simple, portable |

## 9. Distribution

- **GitHub repository**: `codes1gn/workflows`
- **Install**: `pip install -e .`
- **CLI entry point**: `wf`
- **Skills**: copy `builtin-skills/` to `~/.copilot/skills/` or `~/.cursor/skills/`
- **GitHub Pages**: `docs/index.html` at `codes1gn.github.io/workflows`
