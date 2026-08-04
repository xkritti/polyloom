---
description: Start the Polyloom multi-agent software team.
argument-hint: "[goal or issue description]"
skills: polyloom
---

Use the `polyloom` skill for this software-development request.

$ARGUMENTS

## Startup checks

Before delegating, the lead must:

1. Read the team configuration from the plugin data directory (`team.json`).
   If missing, tell the user to run `polyloom_config.py set` for each role.
2. Validate every role entry against the active ZCode provider/model registry.
3. Report the configured `lead`, `builder`, and `runner` model selections to
   the user before starting work.
4. If the user selected different efforts for builder and runner, warn that
   ZCode currently applies effort at the session level and cannot split it
   per child agent.

## Orchestration rules

- Classify the goal. If it is not material software development, answer
  directly without spawning workers.
- Form a short outcome-focused plan before delegation.
- Give each worker a concrete goal, explicit file or module ownership,
  acceptance criteria, validation commands, and expected evidence format.
- Send only relevant context. Do not send the full parent transcript.
- Never assign overlapping write scopes to parallel workers. Parallel write
  scopes are disjoint. Use sequential work when state is shared.
- Worker reports must contain only changed files, checks, failures, and risks.
- If work fails, return it to the same responsible worker with concrete
  evidence. The parent may not fix the implementation.
- Do not deploy, commit, push, merge, or open a pull request unless user authorized.

## Lead constraints

- Lead is coordination-only.
- Never modify repository files from the lead context.
- Do not create a separate reviewer role. The lead reviews worker output.

## Model routing

- Use the `model` alias from `team.json` when invoking child agents.
- The `model` value must match an alias the ZCode runtime can resolve.
- If a model alias is unknown, report the configuration gap immediately.
