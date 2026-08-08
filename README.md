<div align="center">
  <img src="./assets/polyloom-mark.png" width="92" height="92" alt="Polyloom logo">
  <h1>Polyloom</h1>
  <p><strong>One orchestrator. Six purposeful roles. Evidence before done.</strong></p>
  <p>A portable project-local software-development team for Codex and Claude.</p>
  <p>
    <a href="https://github.com/xkritti/polyloom/actions/workflows/validate.yml"><img src="https://img.shields.io/github/actions/workflow/status/xkritti/polyloom/validate.yml?branch=main&amp;style=flat-square&amp;label=validate" alt="Validation status"></a>
    <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-2f8f55?style=flat-square" alt="MIT License"></a>
  </p>
  <p><a href="#why-polyloom">Why Polyloom</a> · <a href="#quick-start">Quick start</a> · <a href="#how-it-works">How it works</a> · <a href="#safety-model">Safety</a></p>
</div>

> [!NOTE]
> Polyloom is an open-source community project. It is not an official OpenAI project.

## Why Polyloom

Polyloom keeps ownership clear: the orchestrator coordinates the whole outcome
while routing work to dev, runner, and independent QA.

| Orchestrator coordinates | Dev builds | Runner accelerates | QA verifies |
| --- | --- | --- | --- |
| Plans, delegates, integrates, reviews, and delivers | Handles coupled, ambiguous, multi-file, and judgment-heavy implementation | Handles narrow, mechanical, repetitive, and high-throughput assignments | Independently verifies code and regressions |

- **One accountable orchestrator:** The orchestrator stays on the critical path from plan to final evidence.
- **Purposeful routing:** Dev handles coupled work; Runner handles bounded work.
- **Safe parallelism:** Workers run together only with explicit, disjoint ownership.
- **Verification built in:** Worker summaries are not proof; QA and the orchestrator review evidence.
- **No surprise publishing:** Deployment, production mutation, commits, pushes, and pull requests require user authorization.

## Quick start

### Requirements

- A Codex runtime and account.
- Python 3.9 or newer for installation.
- Python 3.11 or newer for repository validation.

### 1. Install

```bash
git clone https://github.com/xkritti/polyloom.git polyloom-kit
python3 polyloom-kit/scripts/install.py --scope project --runtime both --project-root /path/to/your-project
```

Run the installer from the kit checkout and point `--project-root` at the
application project. Project mode writes only `.agents/`, `.claude/`,
`.codex/`, and the ownership manifest `.polyloom-install.json` in that target;
it never writes global homes. Remove unchanged owned files safely with
`python3 polyloom-kit/scripts/install.py --scope project --project-root /path/to/your-project --uninstall`.
Use `--scope user --runtime codex` or `--scope user --runtime zcode` only for
legacy compatibility installations.

The legacy Codex user-scope installer copies the skill and compatibility role
definitions into `$CODEX_HOME`, or `~/.codex` when `CODEX_HOME` is unset. It
preserves existing Codex files by refusing to overwrite them unless `--force`
is supplied. The ZCode installer refreshes its plugin cache and updates its
local registration. `scripts/install.py` handles files and registration only;
`scripts/setup.py` optionally persists Codex model/effort and ZCode team
settings when values are supplied through flags or interactive setup.

### 2. Configure

Merge the relevant examples instead of replacing existing configuration:

- [`examples/config.toml`](./examples/config.toml) → `~/.codex/config.toml`
- [`examples/AGENTS.md`](./examples/AGENTS.md) → `~/.codex/AGENTS.md`

These are configuration snippets; copying or merging them is a separate manual
step. Restart Codex or open a new task after changing them.

### 3. Start a team task

Invoke the skill explicitly:

```text
$polyloom

Goal: implement the feature and verify it end to end.
```

With the example global policy installed, software-development prompts starting
with `Goal:` or `/goal`, plus requests such as `use software team`, can load
Polyloom automatically.

## How it works

```mermaid
flowchart LR
    G["Software goal"] --> L["Orchestrator<br/>Plan and delegate"]
    L -->|"Coupled or judgment-heavy"| B["Dev<br/>Senior implementation"]
    L -->|"Narrow or high-throughput"| R["Runner<br/>Bounded worker"]
    B --> I["Orchestrator<br/>Integrate"]
    R --> I
    I --> Q["QA<br/>Independent verification"]
    I --> S["Git/Plane support<br/>On command"]
    Q --> E["Evidence-backed result"]
```

The orchestrator owns orchestration throughout. Dev and Runner receive concrete
goals, explicit ownership, acceptance criteria, validation commands, and an
expected evidence format. They may run in parallel only when write scopes are
disjoint.

## What's included

| Path | Purpose |
| --- | --- |
| [`skills/polyloom/`](./skills/polyloom/) | Codex skill and UI metadata |
| [`agents/lead.toml`](./agents/lead.toml) | Legacy user-scope coordinator compatibility role |
| [`agents/builder-worker.toml`](./agents/builder-worker.toml) | Legacy user-scope implementation compatibility role |
| [`agents/runner-worker.toml`](./agents/runner-worker.toml) | Legacy user-scope bounded-worker compatibility role |
| [`examples/config.toml`](./examples/config.toml) | Parent runtime and concurrency example |
| [`examples/AGENTS.md`](./examples/AGENTS.md) | Minimal global routing policy |
| [`.agents/`](./.agents/) | Project-local six-role contracts |
| [`.claude/`](./.claude/) | Claude project adapter |
| [`.codex/`](./.codex/) | Codex project adapter |
| [`scripts/install.py`](./scripts/install.py) | Dependency-free installer |
| [`scripts/validate.py`](./scripts/validate.py) | Standard-library repository validator |

## Safety model

- The skill cannot change the active parent model by itself.
- The orchestrator coordinates; workers cannot silently take over the team.
- Writing agents must preserve unrelated changes and stay inside assigned ownership.
- High-risk paths stay on the dev/orchestrator route and should receive independent security review.
- The skill does not authorize deployment, production mutation, pushing, merging, or pull-request creation.

## Validate

```bash
python3 scripts/validate.py
```

The validator checks skill metadata, role definitions, and example configuration.

## Contributing

Ideas, issues, and focused pull requests are welcome. Keep routing rules concise,
update examples when behavior changes, and run the validator before submitting a
change.

- Track work in the project's Plane workflow or pull requests; GitHub Issues are not used.
- [View the skill source](./skills/polyloom/SKILL.md)

## License

Polyloom is available under the [MIT License](./LICENSE).
