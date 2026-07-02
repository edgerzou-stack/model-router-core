# model-router-core

A minimal local CLI-first routing core for a `Plan-Act-Review` workflow.

## Goals

- Route `plan` and `review` work to a premium model later.
- Route bounded `execute` work to a cheaper model later.
- Start with simple, stable, rule-based routing.
- Enforce a mandatory human approval gate after `plan`.
- Use mock/stub providers first so workflow behavior is correct before real API integration.

## MVP Scope

- Local Python package
- Rule-based router
- Three-phase workflow: `plan -> approve -> execute -> review`
- Mock provider only
- Basic tests for policy, routing, and workflow gate behavior

## Non-Goals

- Web server
- GUI
- Persistent database
- Real provider integration in the first pass
- Learned or model-based classification

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run tests

```bash
python3 -m unittest discover -s tests
```

## Next milestones

- Add CLI entrypoint
- Add real provider adapters for OpenAI and DeepSeek
- Add config loading
- Add richer escalation policies


## CLI usage

```bash
PYTHONPATH=src python3 -m model_router.cli start --task "Plan this refactor" --id task-001
PYTHONPATH=src python3 -m model_router.cli approve --state .runs/task-001.json --goal "Refactor one module" --in-scope module.py --out-of-scope other.py
PYTHONPATH=src python3 -m model_router.cli execute --state .runs/task-001.json
PYTHONPATH=src python3 -m model_router.cli review --state .runs/task-001.json
PYTHONPATH=src python3 -m model_router.cli show --state .runs/task-001.json
```


## Git / remote

This repository is currently local-only until explicitly initialized as its own git repository and pushed to a remote.
