# implementation_plan

## Approved decisions

- Repository name: `model-router-core`
- Interface: local CLI first
- Routing approach: simple rule-based now, smarter classification later
- Approval policy: mandatory human approval after `plan`
- Provider strategy: mock/stub first

## MVP deliverables

- Core domain types
- Routing and policy layer
- Prompt builders
- Workflow gate for `plan -> approve -> execute -> review`
- Mock provider
- Unit tests
