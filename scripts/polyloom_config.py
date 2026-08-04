#!/usr/bin/env python3
"""Polyloom team configuration CLI."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zcode_config import load_zcode_config, validate_role_config  # noqa: E402

ROLES = ("lead", "builder", "runner")


def provider_enabled(provider: dict) -> bool:
    return provider.get("enabled", True) and not provider.get("systemDisabledReason")


def cmd_list(config: dict) -> int:
    for provider_id, provider in config.get("provider", {}).items():
        if not provider_enabled(provider):
            continue
        for model_id, model in provider.get("models", {}).items():
            variants = model.get("reasoning", {}).get("variants", [])
            print(f"{provider_id}/{model_id}: {','.join(variants) or '(none)'}")
    return 0


def cmd_show(team_path: Path) -> int:
    team = json.loads(team_path.read_text(encoding="utf-8"))
    for role in ROLES:
        entry = team.get(role)
        if entry:
            line = f"{role}: {entry['provider']}/{entry['model']}"
            if entry.get("effort"):
                line += f" ({entry['effort']})"
            print(line)
    return 0


def cmd_set(config: dict, team_path: Path, role: str, provider: str, model: str, effort: str | None) -> int:
    if role not in ROLES:
        print(f"unknown role: {role}; choose from {', '.join(ROLES)}", file=sys.stderr)
        return 1
    entry = config.get("provider", {}).get(provider)
    if entry is None or not provider_enabled(entry):
        print(f"provider unavailable: {provider}", file=sys.stderr)
        return 1
    validate_role_config(config, provider, model, effort)
    team: dict = {}
    if team_path.exists():
        team = json.loads(team_path.read_text(encoding="utf-8"))
    new_entry = {"provider": provider, "model": model}
    if effort is not None:
        new_entry["effort"] = effort
    team[role] = new_entry
    tmp = team_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(team, indent=2) + "\n", encoding="utf-8")
    tmp.replace(team_path)
    print(f"saved {role}: {provider}/{model}")
    return 0


def cmd_validate(config: dict, team_path: Path) -> int:
    from zcode_config import validate_team_config
    team = json.loads(team_path.read_text(encoding="utf-8"))
    validate_team_config(config, team)
    print("Polyloom team configuration is valid.")
    return 0


def cmd_reset(team_path: Path) -> int:
    team_path.unlink(missing_ok=True)
    print("Team configuration reset.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Configure Polyloom roles.")
    p.add_argument("command", choices=("list", "show", "set", "validate", "reset"))
    p.add_argument("--zcode-config", type=Path, required=True)
    p.add_argument("--team", type=Path, required=True)
    p.add_argument("role", nargs="?")
    p.add_argument("provider", nargs="?")
    p.add_argument("model", nargs="?")
    p.add_argument("effort", nargs="?")
    args = p.parse_args(argv)

    try:
        config = load_zcode_config(args.zcode_config)
        if args.command == "list":
            return cmd_list(config)
        if args.command == "reset":
            return cmd_reset(args.team)
        if args.command == "show":
            return cmd_show(args.team)
        if args.command == "validate":
            return cmd_validate(config, args.team)
        if args.command == "set":
            return cmd_set(config, args.team, args.role, args.provider, args.model, args.effort)
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as e:
        print(str(e), file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
