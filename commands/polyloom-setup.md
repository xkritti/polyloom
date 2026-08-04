---
description: Interactive setup wizard for Polyloom team roles.
argument-hint: "[optional goal to preview after setup]"
skills: polyloom
---

Use the `polyloom` skill for this request.

$ARGUMENTS

## Setup wizard

This wizard is ZCode-only. Codex setup selects model and effort only; Codex provider is configured by Codex runtime settings and is not asked here.

Run this wizard when the user has not yet configured `team.json`, or when they
ask to reconfigure the team.

### Steps

For each role in order — `lead`, `builder`, `runner`:

1. Show available providers from the active ZCode config by calling
   `polyloom_config.py list`. Each line shows `provider/model: efforts`.
2. Ask the user to choose a **provider** first.
   Show only enabled providers.
3. After the user picks a provider, show only models under that provider.
   Ask the user to choose a **model**.
4. After the user picks a model, check if that model has reasoning variants.
   If yes, show the supported efforts and ask the user to choose one.
   If no variants exist, skip the effort question.
5. Save by calling:
   ```
   polyloom_config.py set <role> <provider> <model> <effort>
   ```
   Omit `<effort>` if the model has no reasoning variants.

After all three roles are configured:

6. Show a summary table:

   ```
   | Role    | Provider                                | Model         | Effort  |
   |---------|----------------------------------------|---------------|---------|
   | lead    | 1024d7cc-...-db9148943070              | gpt-5.6-sol   | medium  |
   | builder | 1024d7cc-...-db9148943070              | gpt-5.6-terra | high    |
   | runner  | 1024d7cc-...-db9148943070              | gpt-5.6-luna  | low     |
   ```

7. Validate the full team by calling `polyloom_config.py validate`.
8. If valid, confirm the team is ready. If the user provided a goal as
   argument, proceed to orchestrate it using `/polyloom`.

### Rules

- Ask one field at a time: provider, then model, then effort.
- Do not ask all three roles in a single message.
- Only show models from enabled providers.
- Never display API keys or credentials.
- If the user types `skip`, leave that role unconfigured and warn that the
  team is incomplete.
- If the user types `back`, return to the previous question.
- Accept short answers: partial provider ID or model name if unambiguous.
- If the user says "same as builder" for runner, copy the previous selection.
- Respond in the user's language: Thai or English.
- Keep technical identifiers, provider IDs, and model names unchanged.
