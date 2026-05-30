# /deep-research — Workflow Skill

Fan out searches across multiple angles, cross-check findings adversarially, and produce a comprehensive cited report. Equivalent to Claude Code's `/deep-research` workflow.

## Invocation

```
/deep-research <topic or question>
```

Examples:
```
/deep-research transformer architecture advancements 2024
/deep-research state of the art in LLM alignment techniques
/deep-research how does ClickHouse differ from PostgreSQL for analytics
```

## What It Does

Executes a 4-phase workflow:

| Phase | Agents | Mode | Description |
|-------|--------|------|-------------|
| decompose | 1 | sequential | Break topic into 6 research angles |
| search | 6 | parallel | Fan out searches, one agent per angle |
| cross-check | 3 | parallel | Find contradictions, gaps, weak claims |
| synthesize | 1 | sequential | Write comprehensive cited report |

## Agent Rules

When using the `wf` CLI or running this workflow manually:

1. **Start with the decompose phase**: identify 6 distinct angles — do not collapse them
2. **Assign one agent per angle** in the search phase; agents must NOT share work
3. **Cross-check is adversarial**: agents actively try to disprove each other's findings
4. **Synthesize only after cross-check completes**: never merge unverified findings
5. **All claims must be sourced**: prefer primary sources (papers, official docs, authoritative blogs)

## CLI Usage

```bash
# Run via harness
wf run deep-research "transformer architecture advancements 2024"

# Dry run to see plan
wf run deep-research --dry-run "your topic"

# With extra variables
wf run deep-research --var depth=exhaustive "your topic"
```

## Manual Agent Instructions (no CLI)

If the `wf` CLI is not available, run manually:

1. **Ask the user for the topic** (or use `{{query}}` from context)
2. **Phase 1 — Decompose** (1 agent):
   Prompt: *"Generate 6 distinct research angles for: [topic]. Return as JSON: {'angles': [...]}"*
3. **Phase 2 — Search** (6 parallel agents, one per angle):
   Each agent: *"Search the web for: [angle]. Return findings and sources as JSON."*
4. **Phase 3 — Cross-check** (3 parallel agents):
   - Agent 0: find contradictions
   - Agent 1: identify gaps
   - Agent 2: verify sources
5. **Phase 4 — Synthesize** (1 agent):
   *"Write a comprehensive report with inline citations from: [all findings]"*

## Output

The final report includes:
- Executive Summary
- Key Findings with citations
- Conflicting Views
- Confidence Assessment
- References list

## Installation

```bash
cp -r builtin-skills/deep-research ~/.copilot/skills/
# or for Cursor:
cp -r builtin-skills/deep-research ~/.cursor/skills/
```
