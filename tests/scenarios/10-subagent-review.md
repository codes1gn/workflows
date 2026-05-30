# Scenario 10: subagent-review

`builtin-subagents/review.md` defines the Review sub-agent — code review specialist.

## Required Frontmatter

```yaml
name: review
description: Code review agent
model: claude-3-5-sonnet-20241022
tools: [read_file, grep, glob]
permissions:
  allow_write: false
```

## 5 Review Dimensions

1. Security (injection, auth, secrets, OWASP)
2. Performance (N+1, leaks, complexity)
3. Correctness (logic errors, null, races)
4. Maintainability (naming, dead code)
5. Test coverage

## Severity Schema

- `critical`: block merge
- `high`: fix this sprint
- `medium`: backlog
- `low`: optional
