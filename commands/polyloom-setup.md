---
description: Configure legacy ZCode compatibility settings for Polyloom.
argument-hint: "[optional goal to preview after setup]"
skills: polyloom
---

Use the `polyloom` skill for this request.

$ARGUMENTS

## Setup wizard

This wizard is **ZCode-only** and compatibility-only. Project-scoped Codex adapters
already carry the six-role model/effort/sandbox matrix; Claude adapters inherit
Claude's runtime-native configuration. The wizard never displays credentials.
The Codex provider is configured by the Codex runtime, not by this wizard.

Run it when the legacy ZCode `team.json` is missing or when the user explicitly
asks to reconfigure that compatibility path.

### Step 0 - choose scope

Read `team.json` through `polyloom_config.py show`.

- For a new file, configure the three legacy ZCode aliases in this order:
  `lead`, `builder`, `runner`.
- For an existing legacy file, choose `1) Reconfigure one role`,
  `2) Reconfigure all roles`, or `3) Keep current team`.
  Only configure the chosen role when option 1 is selected; leave every other
  role untouched. Leave the other two untouched in a legacy three-role file.
- A team file containing canonical project roles is not a ZCode configuration;
  use the project-scoped Codex adapters instead. Do not mix role sets.

### Step 1 - per-role configuration

For each selected role:

1. Run `polyloom_config.py list` and show only enabled providers and their
   provider/model entries (never API keys).
2. Ask one field at a time: choose a **provider**, then choose a **model**,
   then choose the **effort** when the selected model declares variants.
3. Save with:
   `polyloom_config.py set ROLE PROVIDER MODEL [EFFORT]`.

Accept an unambiguous short answer. `skip` leaves a role unchanged with a
completeness warning; `back` returns to the previous question; `same as <role>`
copies that role's selection.

### Step 2 - summary and validation

Print a summary with role, provider, model, and effort, then run
`polyloom_config.py validate`. If valid, confirm the compatibility team is
ready. If a goal was supplied, continue with `/polyloom`.

Respond in the user's language (Thai or English). Keep technical identifiers,
file paths, commands, and error messages unchanged.
