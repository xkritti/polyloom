---
description: Start the Polyloom six-role software-agent team.
argument-hint: "[goal or issue description]"
skills: polyloom
---

Use the `polyloom` skill for this software-development request.

$ARGUMENTS

## Startup checks

Polyloom project adapters are runtime-native:

The fixed role-specific model, effort, and sandbox matrix below is authoritative.

- Codex loads the six named agents from `.codex/agents/` with the fixed model,
  effort, and sandbox matrix in the skill. The orchestrator is
  `gpt-5.6-sol`/`medium` and `sandbox_mode = "read-only"`; dev is
  `gpt-5.6-luna`/`max`; runner is `gpt-5.6-luna`/`max`; QA is
  `gpt-5.6-terra`/`medium` and read-only; Git and Plane managers are
  `gpt-5.6-luna`/`medium`.
- Claude loads `.claude/agents/` and keeps model/effort selection native to the
  Claude runtime; never add OpenAI model IDs to Claude adapters.
- Legacy ZCode is compatibility-only. If its `team.json` exists, validate the
  team configuration and provider/model registry before using that path and report the configured
  aliases honestly; the legacy model alias is not a project default. It does
  not override project topology or Codex defaults.

Before assigning work, the orchestrator must inspect repository instructions,
current changes, and dependencies, then write a short outcome-focused plan.

## Orchestration rules

- The `orchestrator` is the sole coordinator and final evidence reviewer. Only
  it may assign or spawn core roles. The user may dispatch Git or Plane managers
  directly only for an explicitly requested lifecycle action.
  The orchestrator is coordination-only and remains read-only.
- Give each dispatch a complete payload: **goal**, **exact ownership
  (files/modules)**, **constraints**, **acceptance criteria**, **validation
  commands**, **expected evidence**, and **dependency/order**. Send only
  relevant context; do not send the full parent transcript.
- Dev is autonomous and completes its assigned implementation end to end. Dev
  must not spawn, delegate, assign, route work, or request implementation
  changes from the orchestrator.
- Runner receives detailed, low-judgment executable work and must not design,
  broaden scope, or delegate.
- QA independently reviews read-only and returns `PASS`, `PARTIAL`, or
  `BLOCKED`. Git and Plane managers act only on explicit lifecycle dispatches.
- Never use overlapping write scopes in parallel. If work fails or is blocked,
  report concrete evidence to the orchestrator and return it to the same
  responsible worker; the parent may not fix implementation work.
- When workload and complexity materially benefit from parallelism, the
  orchestrator may spawn 3-7 dev agents with disjoint write scopes; shared-state
  work is sequential.
- Worker reports contain only changed files, checks/results, failures, and
  risks. Review actual diffs and command output before final sign-off.
- Do not deploy, mutate production, commit, push, merge, or open a pull request
  unless the user explicitly authorized that lifecycle action.

## Routing outcome

Classify the goal before spawning. Use dev for coupled implementation, runner
for bounded mechanical work, QA for independent verification, and lifecycle
support only when explicitly requested. The orchestrator owns integration and
the final evidence-backed result; **QA independently reviews** before sign-off.
