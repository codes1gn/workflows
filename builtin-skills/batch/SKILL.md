# /batch — Workflow Skill

Run any task across a list of items in parallel using multiple agents. The batch skill is the general-purpose parallelism primitive — the foundation of all multi-agent workflows.

## Invocation

```
/batch <task description> --items <list>
```

Examples:
```
/batch "translate this file to Spanish" --items file1.md file2.md file3.md
/batch "summarise each PR" --items 42 43 44 45
/batch "migrate each module" --items auth users billing notifications
```

## How It Works

1. **Split**: break the item list into parallel batches
2. **Execute**: spawn one agent per item (up to `max_parallel_agents`)
3. **Collect**: gather all results
4. **Reduce**: optionally merge/summarise results

## CLI Usage

```bash
# Batch process files
wf run batch --var items="file1.py file2.py file3.py" "add type hints to each file"

# Batch with custom parallelism
wf run batch --var items="a b c d e f g h" --var max_parallel=4 "task"
```

## Agent Rules

1. **Items are independent**: each agent gets exactly one item; agents must not share work
2. **Same prompt, different item**: the only variable that changes per agent is the item
3. **Idempotent agents**: agents must produce the same result if run twice (safe to retry)
4. **Fail-fast option**: if `fail_fast=true`, cancel remaining agents on first failure
5. **Result ordering**: results array index corresponds to input item index (order preserved)

## Batch YAML Schema

```yaml
name: my-batch
phases:
  - name: batch
    agents: "{{len(items)}}"
    parallel: true
    prompt_template: |
      Process item {{agent_index}} from: {{items}}
      Task: {{query}}
```

## Output Format

```json
{
  "total_items": N,
  "completed": N,
  "failed": 0,
  "results": [
    {"item": "...", "index": 0, "output": "...", "status": "done"},
    ...
  ]
}
```

## Parallelism Limits

| Setting | Default | Max |
|---------|---------|-----|
| max_parallel_agents | 4 | 16 |
| max_total_agents | 50 | 1000 |

## Retry Behaviour

Failed agents are retried once by default. Set `max_retries=0` to disable retries.
