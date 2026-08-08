<div align="center">
  <img src="./assets/polyloom-mark.png" width="92" height="92" alt="Polyloom logo">
  <h1>Polyloom</h1>
  <p><strong>One lead. Two purpose-built workers. Evidence before done.</strong></p>
  <p>A practical three-role multi-agent software team for Codex: lead, builder, and runner.</p>
  <p>
    <a href="https://github.com/xkritti/polyloom/actions/workflows/validate.yml"><img src="https://img.shields.io/github/actions/workflow/status/xkritti/polyloom/validate.yml?branch=main&amp;style=flat-square&amp;label=validate" alt="Validation status"></a>
    <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-2f8f55?style=flat-square" alt="MIT License"></a>
  </p>
  <p><a href="#why-polyloom">Why Polyloom</a> · <a href="#quick-start">Quick start</a> · <a href="#how-it-works">How it works</a> · <a href="#safety-model">Safety</a></p>
</div>

> [!NOTE]
> Polyloom is an open-source community project. It is not an official OpenAI project.

## Why Polyloom

Polyloom keeps ownership clear: the lead coordinates the whole outcome while
routing bounded work to the worker suited to it.

| Lead coordinates | Builder builds | Runner accelerates |
| --- | --- | --- |
| Plans, delegates, integrates, reviews, and delivers | Handles coupled, ambiguous, multi-file, and judgment-heavy implementation | Handles narrow, mechanical, repetitive, and high-throughput assignments |

- **One accountable lead:** The lead stays on the critical path from plan to final evidence.
- **Purposeful routing:** Builder handles coupled work; Runner handles bounded work.
- **Safe parallelism:** Workers run together only with explicit, disjoint ownership.
- **Verification built in:** Worker summaries are not proof; the lead reviews changes and runs checks.
- **No surprise publishing:** Deployment, production mutation, commits, pushes, and pull requests require user authorization.

## Quick start

### Requirements

- A Codex runtime and account.
- Python 3.9 or newer for installation.
- Python 3.11 or newer for repository validation.

### 1. Install

```bash
git clone https://github.com/xkritti/polyloom.git
cd polyloom
python3 scripts/install.py --runtime codex
```

The Codex installer copies `skills/polyloom/SKILL.md` and the three active role
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
    G["Software goal"] --> L["Lead<br/>Plan and delegate"]
    L -->|"Coupled or judgment-heavy"| B["Builder<br/>Default worker"]
    L -->|"Narrow or high-throughput"| R["Runner<br/>Bounded worker"]
    B --> I["Lead<br/>Integrate and verify"]
    R --> I
    I --> E["Evidence-backed result"]
```

The lead owns orchestration throughout. Builder and Runner receive concrete
goals, explicit ownership, acceptance criteria, validation commands, and an
expected evidence format. They may run in parallel only when write scopes are
disjoint.

## What's included

| Path | Purpose |
| --- | --- |
| [`skills/polyloom/`](./skills/polyloom/) | Codex skill and UI metadata |
| [`agents/lead.toml`](./agents/lead.toml) | Lead role definition |
| [`agents/builder-worker.toml`](./agents/builder-worker.toml) | Builder role definition |
| [`agents/runner-worker.toml`](./agents/runner-worker.toml) | Runner role definition |
| [`examples/config.toml`](./examples/config.toml) | Parent runtime and concurrency example |
| [`examples/AGENTS.md`](./examples/AGENTS.md) | Minimal global routing policy |
| [`scripts/install.py`](./scripts/install.py) | Dependency-free installer |
| [`scripts/validate.py`](./scripts/validate.py) | Standard-library repository validator |

## Safety model

- The skill cannot change the active parent model by itself.
- The lead coordinates; workers cannot silently take over the team.
- Writing agents must preserve unrelated changes and stay inside assigned ownership.
- High-risk paths stay on the Builder/lead route and should receive independent security review.
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

- [Open an issue](https://github.com/xkritti/polyloom/issues)
- [View the skill source](./skills/polyloom/SKILL.md)

## License

Polyloom is available under the [MIT License](./LICENSE).
