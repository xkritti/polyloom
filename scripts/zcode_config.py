from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from team_topology import LEGACY_ZCODE_ROLES


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in {path}") from error


def load_zcode_config(path: Path) -> dict[str, Any]:
    return _load_json(path)


def load_team_config(path: Path, zcode_config: dict[str, Any]) -> dict[str, Any]:
    team = _load_json(path)
    validate_team_config(zcode_config, team)
    return team


def default_team_path(plugin_data_dir: Path) -> Path:
    return plugin_data_dir / "team.json"


def _model(config: dict[str, Any], provider: str, model: str) -> dict[str, Any]:
    try:
        providers = config["provider"]
        provider_data = providers[provider]
        if not provider_data.get("enabled", True) or provider_data.get("systemDisabledReason"):
            raise ValueError(f"provider unavailable: {provider}")
        return provider_data["models"][model]
    except (KeyError, TypeError) as error:
        raise ValueError(f"unknown provider/model: {provider}/{model}") from error


def available_efforts(config: dict[str, Any], provider: str, model: str) -> list[str]:
    """Return only reasoning variants declared by the selected ZCode model."""
    return list(_model(config, provider, model).get("reasoning", {}).get("variants", []))


def validate_role_config(
    config: dict[str, Any], provider: str, model: str, effort: str | None
) -> None:
    _model(config, provider, model)
    if effort is not None and effort not in available_efforts(config, provider, model):
        raise ValueError(f"unsupported effort '{effort}' for {provider}/{model}")


def validate_team_config(config: dict[str, Any], team: dict[str, Any]) -> None:
    if not isinstance(team, dict):
        raise ValueError("team configuration must be an object")
    # ZCode is a compatibility runtime. Its persisted team file intentionally
    # retains the historical three aliases and is independent of project
    # scoped six-role adapters.
    required = set(LEGACY_ZCODE_ROLES)
    roles = set(team)
    missing = required - roles
    unknown = roles - required
    if unknown:
        raise ValueError(f"unknown roles: {', '.join(sorted(unknown))}")
    if missing:
        raise ValueError(f"missing roles: {', '.join(sorted(missing))}")
    for role in sorted(required):
        entry = team[role]
        if not isinstance(entry, dict):
            raise ValueError(f"invalid configuration for role: {role}")
        if "provider" not in entry or "model" not in entry:
            raise ValueError(f"missing provider/model for role: {role}")
        validate_role_config(
            config,
            provider=entry["provider"],
            model=entry["model"],
            effort=entry.get("effort"),
        )


def list_models(config: dict[str, Any]) -> list[dict[str, Any]]:
    """List provider/model/effort entries from ZCode config without credentials."""
    result: list[dict[str, Any]] = []
    for provider_id, provider in config.get("provider", {}).items():
        if not provider.get("enabled", True):
            continue
        if provider.get("systemDisabledReason"):
            continue
        for model_id, model in provider.get("models", {}).items():
            reasoning = model.get("reasoning", {})
            entry = {
                "provider": provider_id,
                "model": model_id,
                "efforts": list(reasoning.get("variants", [])),
            }
            if reasoning.get("defaultVariant"):
                entry["default_effort"] = reasoning["defaultVariant"]
            result.append(entry)
    return result


if __name__ == "__main__":
    raise SystemExit("Import this module; no CLI is defined yet.")
