---
name: polyloom
description: >-
  Run the Polyloom portable project-local software-development team. The
  orchestrator coordinates; dev implements; runner handles bounded work; QA
  independently verifies; git-manager and plane-manager provide on-command
  support. Codex project roles use Luna Max; Claude adapters remain
  runtime-native.
---

# Polyloom

## Runtime configuration

Codex project roles are native custom agents pinned to `gpt-5.6-luna` with
`max` reasoning effort. Claude adapters remain runtime-native and inherit their
own runtime configuration; do not put OpenAI model identifiers in them.

Legacy ZCode user-scope installs are separate: their `team.json` and provider
registry control role aliases and effort settings. Do not apply that legacy
configuration rule to project-scoped Codex or Claude work.

The orchestrator coordinates and reviews evidence while QA independently verifies. The orchestrator is coordination-only and delegates repository mutations to dev or runner. If work fails, return it to the responsible worker.

## Team contract

- `orchestrator` is the sole coordinator and delegates work.
- `dev` is the senior/expert implementation role and may dispatch `runner`.
- `runner` handles narrow, fast, bounded work and may inspect task/PR status.
- `qa` independently reviews and verifies; it is not the orchestrator.
- `git-manager` and `plane-manager` act only when explicitly dispatched.

## Model configuration

- Codex project roles use `gpt-5.6-luna` with `max` reasoning effort; Claude project adapters inherit their runtime configuration.
- Only legacy ZCode user-scope roles use the active provider/model registry and its declared effort variants.
- Never hardcode upstream model names or assume an effort variant exists in legacy configuration.

## Execution

1. Classify the request. Use team mode only for material software-development work.
2. Read repository instructions, confirm the working directory, and inspect existing changes.
3. Write a short goal-focused plan before delegation.
4. Give each worker a concrete goal, explicit file or module ownership, acceptance criteria, validation commands, and expected evidence format.
5. Send only relevant context. Do not send the full parent transcript.
6. Never assign overlapping write scopes to parallel workers. Parallel write scopes are disjoint. Use sequential work when state is shared.
7. Tell workers to preserve unrelated user changes and repository boundaries.
8. Worker reports contain only changed files, checks, failures, and risks.
9. Orchestrator inspects the diff and evidence. Run focused, then risk-appropriate broad checks.
10. If work fails, return it to the same responsible worker with concrete evidence. The parent may not fix the implementation itself.
11. Do not deploy, mutate production, commit, push, merge, or open a pull request unless the user authorized it.

## Language and output

- Respond in the user's language: Thai or English.
- Keep technical identifiers, file paths, commands, and error messages unchanged.
- Report changed files, checks, failures, risks, unsupported behavior, and any action still requiring user approval.
- Do not claim unverified repository checks as live production evidence.

## Scope

Do not use Polyloom for general questions, research, writing-only, operations-only requests, or small fixes where delegation adds no value.

## Evidence rule

A worker summary is not proof. Orchestrator must inspect the resulting changes and run the appropriate verification before reporting completion.
