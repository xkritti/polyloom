# AGENTS.md

Project-local guidance for Polyloom's runtime-neutral adapters. These contracts
are generic software-development instructions; product-specific rules may be
supplied as an overlay.

## Team contract

One accountable `orchestrator` coordinates work. The hierarchy is
`orchestrator` -> `dev`, `qa`, and `runner`; `dev` may delegate bounded work to
`runner`. QA validates independently and reports evidence to the orchestrator.
`git-manager` and `plane-manager` are on-command support roles.

Codex custom roles are pinned to `gpt-5.6-luna` with `max` reasoning effort.
Claude adapters remain runtime-native and inherit their model configuration;
never put an OpenAI model identifier in a Claude adapter.

## Scope and safety

Own only assigned files, preserve concurrent edits, follow repository
architecture and tests, and report changed files, checks, failures, and risks.
Do not deploy, mutate production, or perform lifecycle actions without an
explicit request.
