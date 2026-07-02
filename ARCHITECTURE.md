# Architecture

## Layers

### 1. Playbook
The playbook is the operating constitution.
It defines `plan first`, `human approval`, `execution discipline`, and `review plus memory reporting`.
It is a workflow policy, not the engine implementation.

### 2. Router Core
This repository is the engine.
It decides task class, phase, escalation, and approval gating.
It owns the domain types, routing policy, prompt contracts, and workflow state transitions.

### 3. Skill Layer
A skill is an instruction wrapper for an agent.
It explains when to use the router and how to interact with it.
It should not hold the main executable business logic.

### 4. Provider Layer
Providers translate a router request into a concrete model call.
The MVP uses only a mock provider.
Future versions can add `OpenAIProvider` and `DeepSeekProvider` without changing router policy.

## Workflow

```text
User Task
  -> classify task
  -> PLAN
  -> require human approval
  -> EXECUTE
  -> REVIEW
```

## First-pass design decisions

- Keep routing deterministic and rule-based.
- Make approval after `plan` mandatory.
- Keep provider logic behind a stable interface.
- Prefer explicit handoff packets over hidden context.
- Escalate ambiguity instead of guessing.
