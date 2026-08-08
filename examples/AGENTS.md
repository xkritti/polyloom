## Polyloom

Main Codex is the orchestrator. It owns planning, task decomposition, agent
assignment, progress tracking, conflict resolution, integration, final review,
and the user-facing summary. Do not delegate orchestration itself.

When software-team mode applies, load and follow
`$polyloom`.

Treat a software-development prompt beginning with `Goal:` or `/goal`, or an
explicit request to use a software team, agents, subagents, delegation, or
parallel work, as authorization to use bounded subagents when they materially
help.

Use `dev` for senior coupled implementation and `runner` for narrow,
mechanical work with explicit acceptance criteria. `qa` independently
verifies; `git-manager` and `plane-manager` act only on command.

Give every writing agent explicit file or module ownership, expected output,
validation commands, and disjoint write scope. Keep the parent on the critical
path, review every worker change, and verify the integrated result before
calling the task complete.
