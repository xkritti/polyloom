@../.agents/AGENTS.md

Polyloom's Claude adapter uses the six generic role contracts in `.agents/`.
Claude keeps its own runtime-native model and effort configuration; do not add
OpenAI model IDs here. The `orchestrator` is the sole coordinator, `dev` is
autonomous, `runner` is bounded, `qa` is read-only, and Git/Plane managers are
on-command lifecycle support.
