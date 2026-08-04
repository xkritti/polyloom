# Polyloom ZCode MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a ZCode plugin that preserves Solweaver's three-role workflow while letting the user select a real ZCode provider, model, and supported effort for Lead, Builder, and Runner.

**Architecture:** Keep Polyloom as a native ZCode plugin containing one skill and one `/polyloom` command. A small dependency-free Python helper reads ZCode's real model registry, validates a plugin-owned `team.json`, and produces the role configuration consumed by the workflow. Lead coordinates and reviews only; Builder and Runner own all repository writes.

**Tech Stack:** ZCode plugin manifest, Markdown skills/commands, Python 3.11 standard library, pytest, JSON.

## Global Constraints

- Preserve exactly three roles: `lead`, `builder`, `runner`.
- Lead may inspect and verify but must never modify repository files.
- Lead performs review; do not introduce a separate reviewer role.
- Provider/model/effort values must come from the live ZCode registry, never a hard-coded catalog.
- Omit effort when a model exposes no `reasoning.variants`.
- User-facing output follows the user's Thai or English; identifiers, paths, commands, and errors remain unchanged.
- Follow strict RED-GREEN-REFACTOR for every behavior.
- Do not push, publish, or install globally without explicit user authorization.

---

### Task 1: Correct the inherited Solweaver contract

**Files:**
- Modify: `skills/polyloom/SKILL.md`
- Test: `tests/test_polyloom_skill.py`

**Interfaces:**
- Consumes: existing Polyloom skill copied from Solweaver.
- Produces: a consistent three-role contract used by the ZCode command and runtime tests.

- [ ] **Step 1: Add failing assertions**

Assert that the skill contains no `Sol`, `Terra`, `Luna`, `reviewer`, `security_reviewer`, `tester`, or `code_mapper` routing; says Builder/Runner own all writes; says Lead sends failures back to the responsible worker and never fixes them directly.

- [ ] **Step 2: Verify RED**

Run:
```bash
python -m pytest tests/test_polyloom_skill.py -q
```
Expected: FAIL because inherited extra roles and parent-write fallback remain.

- [ ] **Step 3: Apply the minimal contract cleanup**

Keep only Lead, Builder, Runner. Replace inherited `Terra and Luna` wording. Remove independent-reviewer routing and the sentence permitting the parent to fix failed work.

- [ ] **Step 4: Verify GREEN**

Run:
```bash
python -m pytest tests/test_polyloom_skill.py -q
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/polyloom/SKILL.md tests/test_polyloom_skill.py
git commit -m "refactor: preserve Polyloom three-role contract"
```

### Task 2: Complete live provider/model/effort discovery

**Files:**
- Modify: `scripts/zcode_config.py`
- Test: `tests/test_zcode_config.py`
- Test: `tests/test_zcode_config_loader.py`

**Interfaces:**
- Consumes: ZCode `config.json` provider registry.
- Produces: `list_available_models(config) -> list[dict]`, `available_efforts(config, provider, model) -> list[str]`, and strict role validation.

- [ ] **Step 1: Write failing discovery tests**

Cover enabled providers, disabled providers, missing models, duplicate model names under different providers, model-specific effort variants, and models with no effort support. Assert API keys are never returned.

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/test_zcode_config.py tests/test_zcode_config_loader.py -q
```
Expected: FAIL because catalog discovery and provider eligibility checks are absent.

- [ ] **Step 3: Implement minimal discovery**

Return only provider ID, provider display name, model ID, model display name, enabled state, and effort variants. Reject disabled providers and `systemDisabledReason` entries during team validation.

- [ ] **Step 4: Verify GREEN**

```bash
python -m pytest tests/test_zcode_config.py tests/test_zcode_config_loader.py -q
```
Expected: PASS with no credentials in test output.

- [ ] **Step 5: Commit**

```bash
git add scripts/zcode_config.py tests/test_zcode_config.py tests/test_zcode_config_loader.py
git commit -m "feat: discover ZCode models and efforts"
```

### Task 3: Add a user-facing team configuration CLI

**Files:**
- Create: `scripts/polyloom_config.py`
- Create: `tests/test_polyloom_config_cli.py`
- Create: `examples/team.json`

**Interfaces:**
- Consumes: `~/.zcode/v2/config.json`, plugin data directory, and command arguments.
- Produces: `list`, `show`, `set`, and `validate` CLI operations over `team.json`.

- [ ] **Step 1: Write failing CLI tests**

Use temporary files and subprocess calls. Verify:
```text
polyloom_config.py list
polyloom_config.py set lead PROVIDER MODEL EFFORT
polyloom_config.py show
polyloom_config.py validate
```
Assert unsupported effort exits non-zero, valid settings persist atomically, and output never includes API keys.

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/test_polyloom_config_cli.py -q
```
Expected: FAIL because the CLI does not exist.

- [ ] **Step 3: Implement the minimum CLI**

Use `argparse`, `json`, and `Path.replace()` for atomic writes. Resolve defaults from `ZCODE_PLUGIN_DATA` and `~/.zcode/v2/config.json`; allow explicit paths for tests.

- [ ] **Step 4: Verify GREEN**

```bash
python -m pytest tests/test_polyloom_config_cli.py -q
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/polyloom_config.py tests/test_polyloom_config_cli.py examples/team.json
git commit -m "feat: configure Polyloom team models"
```

### Task 4: Prove how ZCode selects a model per child agent

**Files:**
- Create: `docs/zcode-agent-model-spike.md`
- Create: `tests/test_zcode_agent_capability.py`
- Potentially modify after evidence: `.zcode-plugin/plugin.json`, `commands/polyloom.md`, or add a minimal MCP bridge under `mcp/`.

**Interfaces:**
- Consumes: installed ZCode runtime and actual subagent metadata/transcripts.
- Produces: an executable capability result: native per-child model override, or a documented bridge requirement.

- [ ] **Step 1: Write a failing capability test**

The test must require captured runtime evidence containing child role, provider, model, and effort for two children using different configurations. A missing field is failure, not skip.

- [ ] **Step 2: Inspect the real ZCode agent/spawn interface**

Use installed plugin examples, CLI help, runtime files, and a disposable ZCode task. Do not infer API fields from Codex TOML.

- [ ] **Step 3: Implement the smallest proven route**

Preferred order:
1. Native ZCode child-agent model/effort override.
2. Native profile definitions generated from `team.json`.
3. Minimal plugin MCP bridge only if native configuration cannot express the override.

- [ ] **Step 4: Verify GREEN with a real run**

Spawn Builder and Runner using different configured models/efforts. Capture runtime evidence and make `tests/test_zcode_agent_capability.py` pass.

- [ ] **Step 5: Commit**

```bash
git add docs/zcode-agent-model-spike.md tests/test_zcode_agent_capability.py .zcode-plugin commands mcp 2>/dev/null || true
git commit -m "feat: route Polyloom workers to configured models"
```

### Task 5: Connect `/polyloom` to real orchestration

**Files:**
- Modify: `commands/polyloom.md`
- Modify: `skills/polyloom/SKILL.md`
- Create: `tests/test_polyloom_orchestration.py`

**Interfaces:**
- Consumes: validated `team.json` and the proven child-agent route from Task 4.
- Produces: Goal → Lead plan → Builder/Runner execution → Lead review/verification → final evidence.

- [ ] **Step 1: Write failing orchestration tests**

Test prompt contract generation for Builder and Runner, disjoint ownership, concise context, Thai/English output selection, and Lead write prohibition. Test that failed evidence returns to the same worker.

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/test_polyloom_orchestration.py -q
```
Expected: FAIL because orchestration binding is incomplete.

- [ ] **Step 3: Implement minimal binding**

Make `/polyloom` load the team config, reject invalid roles before spawning, send bounded contracts, and require changed files/checks/failures/risks from workers.

- [ ] **Step 4: Verify GREEN**

```bash
python -m pytest tests/test_polyloom_orchestration.py -q
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add commands/polyloom.md skills/polyloom/SKILL.md tests/test_polyloom_orchestration.py
git commit -m "feat: orchestrate Polyloom team in ZCode"
```

### Task 6: Build safe installer and plugin validator

**Files:**
- Modify: `scripts/install.py`
- Modify: `scripts/validate.py`
- Create: `tests/test_install_zcode.py`
- Modify: `.github/workflows/validate.yml`

**Interfaces:**
- Consumes: repository plugin bundle.
- Produces: no-overwrite local installation and CI validation.

- [ ] **Step 1: Write failing installer tests**

Verify install into a temporary ZCode plugin directory, refusal to overwrite, complete copying of manifest/commands/skills/scripts, and no mutation of `~/.zcode/v2/config.json`.

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/test_install_zcode.py -q
```
Expected: FAIL because the inherited installer targets Codex.

- [ ] **Step 3: Implement minimal ZCode installer**

Install the plugin bundle into an explicit destination or the documented ZCode user plugin path. Keep no-overwrite behavior. Remove Codex-only install instructions from the default path.

- [ ] **Step 4: Expand validator and CI**

Validate plugin JSON, command frontmatter, skill frontmatter, three-role invariant, Python syntax, and full pytest suite.

- [ ] **Step 5: Verify GREEN**

```bash
python -m pytest tests -q
python scripts/validate.py
```
Expected: all tests and validation pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/install.py scripts/validate.py tests/test_install_zcode.py .github/workflows/validate.yml
git commit -m "feat: install and validate Polyloom for ZCode"
```

### Task 7: Run end-to-end ZCode acceptance

**Files:**
- Create: `tests/fixtures/polyloom-smoke-project/README.md`
- Create: `docs/acceptance.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: installed Polyloom plugin and three configured models.
- Produces: evidence that the plugin works in ZCode, not only under unit tests.

- [ ] **Step 1: Install into a disposable ZCode scope**

Install Polyloom without changing existing user plugins. Restart or reload ZCode as required.

- [ ] **Step 2: Configure distinct roles**

Choose valid live provider/model/effort combinations for Lead, Builder, and Runner from the current registry.

- [ ] **Step 3: Execute a bilingual smoke goal**

Use `/polyloom` on a disposable repository task containing one coupled change and one disjoint mechanical change. The user prompt should be Thai with English identifiers.

- [ ] **Step 4: Verify acceptance evidence**

Require all of:
- Lead made no repository writes.
- Builder and Runner used the configured provider/model/effort.
- Worker scopes were disjoint.
- Lead inspected diff and ran checks.
- Final response followed the user's language.
- Token usage for each child was recorded.

- [ ] **Step 5: Update README with only verified behavior**

Document installation, configuration, invocation, limitations, attribution to Solweaver, and actual acceptance output. Remove upstream Codex-only claims and benchmarks that do not measure Polyloom.

- [ ] **Step 6: Final verification and commit**

```bash
python -m pytest tests -q
python scripts/validate.py
git status --short
git diff --check
git add README.md docs/acceptance.md tests/fixtures
git commit -m "docs: document verified Polyloom workflow"
```

## Definition of Done

Polyloom is usable only when all conditions are true:

- ZCode installs and discovers the plugin.
- `/polyloom` appears and loads the skill.
- User can list actual ZCode providers/models and supported efforts without exposing credentials.
- User can assign valid provider/model/effort independently to Lead, Builder, and Runner.
- A real ZCode run proves the configured model and effort for each child.
- Lead performs no source writes and reviews/verifies worker output.
- Builder and Runner complete bounded work successfully.
- Thai input receives natural Thai output while technical text remains unchanged.
- Full tests, validator, and end-to-end acceptance pass.
- README describes verified behavior only.

## Current Status

Completed foundation:
- Fork at `xkritti/polyloom`.
- ZCode manifest, `/polyloom` command, Polyloom skill.
- JSON/team validation and model-specific effort validation.
- Current suite: 21 passing tests.

Critical path remaining:
1. Correct inherited contract drift.
2. Prove per-child model/effort control in live ZCode.
3. Bind orchestration.
4. Install and run end-to-end acceptance.
