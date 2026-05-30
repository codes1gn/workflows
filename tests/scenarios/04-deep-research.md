# Scenario 04: deep-research

Verifies that `deep-research.yaml` correctly implements the 4-phase fan-out research workflow matching Claude Code's `/deep-research` built-in.

## Expected Phases

| Phase | Agents | Parallel | Key Elements |
|-------|--------|----------|-------------|
| decompose | 1 | false | Break query into 6 angles |
| search | 6 | true | One agent per angle |
| cross-check | 3 | true | Contradictions, gaps, source verification |
| synthesize | 1 | false | Cited report with executive summary |

## Checks

1. `decompose` phase present
2. `search` phase present
3. `cross-check` phase present
4. `synthesize` phase present
5. At least one phase has `parallel: true`
6. `agents: 6` for the search phase
7. `{{query}}` variable used in prompt templates

## Pass Criteria

Workflow implements full 4-phase fan-out research matching Claude Code's design.
