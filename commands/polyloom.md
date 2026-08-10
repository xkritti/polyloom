---
description: Start the Polyloom multi-agent software team.
argument-hint: "[goal or issue description]"
skills: polyloom
---

Use the `polyloom` skill for this software-development request.

$ARGUMENTS

## Startup checks

Codex project roles are native custom agents pinned to Luna Max; Claude project
adapters use their native runtime configuration. Neither requires `team.json`.
Only the legacy ZCode user-scope path uses
`team.json` and provider registry validation.

Before delegating, the orchestrator must:

1. For project-scoped Codex work, spawn the named role from `.codex/agents/`; every role uses `gpt-5.6-luna` with `max` effort. For Claude work, use the native adapter files in the project.
2. (Legacy ZCode only) Read the team configuration from the plugin data directory (`team.json`).
   If missing, tell the user to run `polyloom_config.py set` for each role.
3. Validate every legacy ZCode role entry against the active provider/model registry.
4. Report configured legacy ZCode role selections to
   the user before starting work.
5. If the user selected different efforts for legacy roles, warn that
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

## Orchestrator constraints

- Orchestrator is coordination-only; QA independently verifies.
- Never modify repository files from the orchestrator context.
- QA independently reviews worker output; the orchestrator coordinates.

## Legacy ZCode model routing

- Use the `model` alias from `team.json` when invoking child agents.
- The `model` value must match an alias the ZCode runtime can resolve.
- If a model alias is unknown, report the configuration gap immediately.
