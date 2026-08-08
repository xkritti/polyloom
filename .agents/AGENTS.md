# AGENTS.md

Context for AI agents working on this repository (**Polyloom** — a
multi-agent software team skill for ZCode/Codex). Read this before making
changes so your work fits the project's structure and conventions.

## What this repo is

Polyloom ships a multi-agent software team for ZCode. It keeps one accountable
lead (`lead`) routing bounded work to two workers (`builder` and `runner`).
The repo is the **source of the skill itself** — the agent definitions, skill
file, commands, installer, and tests that get installed into a ZCode runtime.

## Project layout

| Path | Purpose |
| --- | --- |
| `agents/*.toml` | ZCode/Codex runtime agent definitions (lead, builder, runner) |
| `skills/polyloom/` | The Polyloom skill (`SKILL.md`, agent metadata) |
| `commands/` | ZCode slash commands (`polyloom.md`, `polyloom-setup.md`) |
| `scripts/` | Installer, setup wizard, and config CLIs (`install.py`, `setup.py`, `polyloom_config.py`, `zcode_config.py`, `validate.py`) |
| `examples/` | `config.toml` and `AGENTS.md` examples for users |
| `tests/` | `pytest` test suite |
| `docs/` | Design docs and spikes |
| `.zcode-plugin/` | ZCode plugin metadata |

## Development conventions

- **Python** for all scripts. Target Python 3.9+ for installed tooling, 3.11+
  for repository validation.
- Keep installed tooling dependency-free (standard library only) so it works
  anywhere.
- Preserve the team-contract shape: one `lead`, one `builder`, one `runner`.
  Do not add a separate reviewer role.
- Model/provider/effort selections are resolved from the active ZCode
  registry at runtime (`team.json`); do not hardcode upstream model names.
- When behavior changes, update the `examples/` and the skill docs to match.

## Validation

Run the repository validator (same as CI):

```bash
python3 scripts/validate.py
```

Run the test suite:

```bash
python3 -m pytest
```

## Boundaries

- Tests and validation must pass before reporting work complete.
- Do not deploy, commit, push, merge, or open a pull request unless authorized.