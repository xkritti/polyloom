@../.agents/AGENTS.md

Project-local role adapters live in `.claude/agents/` and share the generic
contracts in `.agents/`. Use `orchestrator`, `dev`, and `runner` for
software work; use `qa` for independent validation; invoke `git-manager` and
`plane-manager` only for explicitly requested lifecycle actions. Product
instructions may overlay these generic software-development contracts.
