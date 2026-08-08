# AGENTS.md

Project-local guidance for Polyloom's runtime-neutral adapters. These contracts
are generic software-development instructions; product-specific rules may be
supplied as an overlay.

## Team contract

One accountable `orchestrator` coordinates work. The hierarchy is
`orchestrator` -> `dev`, `qa`, and `runner`; `dev` may delegate bounded work to
`runner`. QA validates independently and reports evidence to the orchestrator.
`git-manager` and `plane-manager` are on-command support roles.

Runtime provider, model, and effort inherit from the active parent session and
team configuration. Do not pin those values in project-local adapters.

## Scope and safety

Own only assigned files, preserve concurrent edits, follow repository
architecture and tests, and report changed files, checks, failures, and risks.
Do not deploy, mutate production, or perform lifecycle actions without an
explicit request.
