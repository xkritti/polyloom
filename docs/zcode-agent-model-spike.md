# ZCode Agent Model Selection — Spike Results

Date: 2026-08-04

## Question

Can ZCode spawn child agents with a different model, provider, and reasoning
effort per agent?

## Evidence

Inspected `/Users/0xsolid-pyh/.zcode/cli/agents/` runtime metadata files.

### Agent metadata structure

Each child agent has `metadata.json` with:

```
agentId, childSessionId, createdAt, cwd, description, profileId,
profileSnapshot { name, description, color, source, systemPrompt, tools },
prompt, status, workspaceRoot, completedAt, totalDurationMs,
totalTokens, totalToolUseCount, usage { inputTokens, outputTokens, ... }
```

### Model override is real

Two agents in session `sess_e3cbc535-...` have an extra key inside
`profileSnapshot`:

```json
{
  "profileId": "Explore",
  "profileSnapshot": {
    "name": "Explore",
    "model": "lite"
  }
}
```

Both agents use the built-in `Explore` profile but override `model` to `lite`.
No other metadata field carries model or provider information.

### Profile fields available

`profileSnapshot` can carry at minimum:

- `name` — display name
- `description` — human-readable role description
- `color` — UI accent
- `source` — `built-in` or plugin
- `systemPrompt` — system instructions
- `tools` — list of allowed tool names
- `model` — model override (confirmed)

### What is NOT present

- No `provider` field in `profileSnapshot`.
- No `effort` or `reasoning_effort` field in `profileSnapshot`.
- `config.json` has only `provider` registry; no `profiles` section.
- ZCode plugin manifests do not declare `profiles` or `agents` fields.
- The `model` value is a short alias (`lite`), not a full provider/model path.

## Interpretation

ZCode supports per-child model override via `profileSnapshot.model`.

However:

1. The override uses a model alias, not a provider-qualified path.
2. There is no evidence of per-child `effort` override in metadata.
3. Plugin manifests cannot declare profiles; the runtime builds them.
4. The `model` alias maps to a model entry in `config.json`, but the mapping
   is not exposed as a public schema.

## Conclusion

Native per-child model override exists but is partial:

- Model: supported via `profileSnapshot.model` (alias-based).
- Provider: not directly addressable; determined by model alias resolution.
- Effort: not addressable per child via `profileSnapshot`.

For Polyloom to route Builder and Runner to different models, Polyloom must
generate agent profiles that carry a `model` alias matching the user's
selection. Effort override per child is not available through this path.

## Next step

Since ZCode's plugin API does not expose profile creation, Polyloom should:

1. Define Builder and Runner as agent profiles in the SKILL.md contract.
2. Use the `model` alias from `team.json` when invoking child agents.
3. Accept that effort override stays at the session level and cannot be
   split per child until ZCode adds that capability.
4. Document this limitation in the skill so Lead reports the gap honestly
   when the user selects different efforts for Builder and Runner.

This keeps Polyloom honest about what ZCode can actually do.
