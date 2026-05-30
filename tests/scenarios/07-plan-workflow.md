# Scenario 07: plan-workflow

`plan.yaml` implements a 4-phase adversarial planning workflow.

## Phases

| Phase | Agents | Parallel | Description |
|-------|--------|----------|-------------|
| understand | 1 | false | Problem, success criteria, constraints |
| explore | 3 | true | Conventional / ambitious / pragmatic approaches |
| challenge | 3 | true | Adversarially poke holes in each approach |
| synthesize | 1 | false | Recommended plan with mitigations |

## Key Design: Adversarial Review

The `challenge` phase is the distinguishing feature. Each agent challenges the corresponding `explore` approach, asking:
- What are the failure modes?
- What assumptions could be wrong?
- What are the hidden costs?
