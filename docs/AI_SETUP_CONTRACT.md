# AI Setup Contract

When an AI agent is asked to help a user set up this repository, it should follow this order:

1. Run `model-router doctor` first.
2. If config is missing, instruct the user to run `model-router init`.
3. If environment variables are missing, explicitly ask the user to provide or export them.
4. Do not start execution until readiness is `READY`.
5. Use `model-router run --task "..."` to begin a task.
6. Stop after `plan` and wait for explicit human approval.
7. Use `approve`, `execute`, and `review` as explicit follow-up steps.
