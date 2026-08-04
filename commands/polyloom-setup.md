---
description: Interactive setup wizard for Polyloom team roles.
argument-hint: "[optional goal to preview after setup]"
skills: polyloom
---

Use the `polyloom` skill for this request.

$ARGUMENTS

## Setup wizard

This wizard is ZCode-only. Codex setup selects model and effort only; Codex provider is configured by Codex runtime settings and is not asked here.

Run this wizard when:
- `team.json` does not exist (first-time setup), or
- the user asks to reconfigure a role, or
- the user asks to reconfigure the whole team.

### Step 0 — decide scope

Read `team.json` (via `polyloom_config.py show`).

- If `team.json` does not exist or is empty, run **full setup** for all three roles: `lead`, `builder`, `runner`.
- If `team.json` already has entries, ask the user:

  ```
  1) Reconfigure one role
  2) Reconfigure all roles
  3) Keep current team
  ```

- If the user picks `1`, ask which role:

  ```
  1) lead (current: provider/model/effort)
  2) builder (current: provider/model/effort)
  3) runner (current: provider/model/effort)
  ```

  Only configure the chosen role. Leave the other two untouched.
- If the user picks `2`, run full setup for all three roles in order.
- If the user picks `3`, skip setup entirely.

### Step 1 — per-role configuration

For each role that will be configured (either the single chosen role, or all three in order: `lead`, `builder`, `runner`):

1. Show available providers from the active ZCode config by calling `polyloom_config.py list`. Each line shows `provider/model: efforts`.
2. Ask the user to choose a **provider** first. Show only enabled providers.
3. After the user picks a provider, show only models under that provider. Ask the user to choose a **model**.
4. After the user picks a model, check if that model has reasoning variants. If yes, show the supported efforts and ask the user to choose one. If no variants exist, skip the effort question.
5. Save by calling:
   ```
   polyloom_config.py set <role> <provider> <model> <effort>
   ```
   Omit `<effort>` if the model has no reasoning variants.

### Step 2 — summary and validation

After configuration is done:

6. Show a summary table:

   ```
   | Role    | Provider | Model         | Effort  |
   |---------|----------|---------------|---------|
   | lead    | ...      | gpt-5.6-sol   | medium  |
   | builder | ...      | gpt-5.6-terra | high    |
   | runner  | ...      | gpt-5.6-luna  | low     |
   ```

7. Validate the full team by calling `polyloom_config.py validate`.
8. If valid, confirm the team is ready. If the user provided a goal as argument, proceed to orchestrate it using `/polyloom`.

### Rules

- Ask one field at a time: provider, then model, then effort.
- Do not ask all three roles in a single message when reconfiguring one role.
- Only show models from enabled providers.
- Never display API keys or credentials.
- If the user types `skip`, leave that role unchanged and warn that the team may be incomplete.
- If the user types `back`, return to the previous question.
- Accept short answers: partial provider ID or model name if unambiguous.
- If the user says "same as builder" for runner, copy the previous selection.
- Respond in the user's language: Thai or English.
- Keep technical identifiers, provider IDs, and model names unchanged.
