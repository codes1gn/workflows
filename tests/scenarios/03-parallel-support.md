# Scenario 03: parallel-support

The WorkflowRunner implements parallel agent execution using Python's `concurrent.futures.ThreadPoolExecutor`.

## Implementation Requirements

- Import `concurrent.futures`
- Use `ThreadPoolExecutor` for parallel phases
- Enforce `MAX_PARALLEL = 16` (hard cap, matching Claude Code)
- Enforce `MAX_TOTAL = 1000` (hard cap, matching Claude Code)

## Design

```python
with concurrent.futures.ThreadPoolExecutor(max_workers=effective_parallel) as pool:
    futures = {pool.submit(run_agent, i): i for i in range(num_agents)}
    for fut in concurrent.futures.as_completed(futures):
        result = fut.result()
```

## Checks

All checks inspect `workflow_runner/runner.py` source code for required patterns.
