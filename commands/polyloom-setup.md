---
description: Interactive setup wizard for Polyloom team roles.
argument-hint: "[optional goal to preview after setup]"
skills: polyloom
---

Use the `polyloom` skill for this request.

$ARGUMENTS

## Setup wizard

Run this wizard when the user has not yet configured `team.json`, or when they
ask to reconfigure the team.

### Steps

For each role in order — `lead`, `builder`, `runner`:

1. Show the list of available models from the active ZCode provider registry.
   Call `polyloom_config.py list` to get the current catalog.
2. Ask the user which model to use for this role.
   Accept the provider/model pair, e.g. `1024d7cc.../gpt-5.6-sol`.
3. If the selected model has reasoning variants, ask which effort to use.
   Show only the supported variants for that model.
   If the model has no reasoning variants, skip the effort question.
4. Save the selection by calling:
   ```
   polyloom_config.py set <role> <provider> <model> <effort>
   ```

After all three roles are configured:

5. Show a summary table:

   ```
   | Role    | Provider | Model         | Effort  |
   |---------|----------|---------------|---------|
   | lead    | ...      | gpt-5.6-sol   | medium  |
   | builder | ...      | gpt-5.6-terra | high    |
   | runner  | ...      | gpt-5.6-luna  | low     |
   ```

6. Validate the full team by calling `polyloom_config.py validate`.
7. If valid, confirm the team is ready. If the user provided a goal as
   argument, proceed to orchestrate it using `/polyloom`.

### Rules

- One question at a time. Do not ask all three roles in a single message.
- Only show models from enabled providers.
- Never display API keys or credentials.
- If the user types `skip`, leave that role unconfigured and warn that the
  team is incomplete.
- If the user types `back`, return to the previous role question.
- Accept short answers: model name without provider prefix if unambiguous.
- If the user says "same as builder" for runner, copy the previous selection.
- Respond in the user's language: Thai or English.
- Keep technical identifiers, model names, and provider IDs unchanged.
