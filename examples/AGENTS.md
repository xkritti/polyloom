## Polyloom project policy

The project `orchestrator` is the sole coordinator, integrator, and final
reviewer. It is read-only and is the only role allowed to assign or spawn core
roles. The user may dispatch Git or Plane managers directly only for an
explicit lifecycle action. Load and
follow `$polyloom` for material software-development work.

The six project roles are `orchestrator`, `dev`, `runner`, `qa`,
`git-manager`, and `plane-manager`. Dev is autonomous and completes its
assigned outcome end to end without delegation. Runner performs detailed,
low-judgment bounded work. QA independently verifies in read-only mode. Git
and Plane managers act only on explicit lifecycle dispatch.

Each dispatch must state the goal, exact ownership (files/modules),
constraints, acceptance criteria, validation commands, expected evidence, and
dependency/order. Send relevant context only, never the full parent
transcript. The orchestrator may spawn 3-7 dev agents when workload and
complexity materially benefit; keep parallel write scopes disjoint, shared
state sequential, and return blocked work to the same responsible owner.

Workers report only changed files, checks/results, failures, and risks. The
orchestrator reviews evidence before sign-off and never edits repository files.
Do not deploy, mutate production, commit, push, merge, or open a pull request
without explicit user authorization.
