#!/usr/bin/env python3
"""Interactive Polyloom installer and runtime setup wizard.

ZCode setup asks provider/model/effort. Codex setup asks model/effort only;
Codex provider is configured by Codex runtime settings. Never print credentials.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"
ROLES = ("lead", "builder", "runner")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Install Polyloom and configure ZCode or Codex.")
    p.add_argument("--runtime", choices=("zcode", "codex", "both"), default=None)
    p.add_argument("--target", type=Path, default=None)
    p.add_argument("--team", type=Path, default=None)
    p.add_argument("--zcode-config", type=Path, default=Path.home() / ".zcode/v2/config.json")
    p.add_argument("--force", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--interactive", action="store_true")
    p.add_argument("--non-interactive", action="store_true")
    p.add_argument("--lead")
    p.add_argument("--builder")
    p.add_argument("--runner")
    p.add_argument("--codex-model")
    p.add_argument("--codex-effort")
    p.add_argument("--codex-provider", help=argparse.SUPPRESS)
    return p


def ask_runtime() -> str:
    while True:
        value = input("Install for [zcode/codex/both]: ").strip().lower()
        if value in {"zcode", "codex", "both"}:
            return value
        print("Choose zcode, codex, or both.")


def split_selection(value: str) -> tuple[str, str, str | None]:
    parts = value.split("/", 2)
    if len(parts) not in (2, 3):
        raise ValueError("selection must be provider/model[/effort]")
    return parts[0], parts[1], parts[2] if len(parts) == 3 else None


def run_install(runtime: str, target: Path | None, force: bool, dry_run: bool) -> None:
    if dry_run:
        print(f"[dry run] install {runtime}")
        return
    command = [sys.executable, str(INSTALL), "--runtime", runtime]
    if target:
        command += ["--target", str(target)]
    if force:
        command.append("--force")
    subprocess.run(command, check=True)


def configure_zcode(args: argparse.Namespace, team: Path, dry_run: bool) -> None:
    selections: dict[str, dict[str, str]] = {}
    values = {role: getattr(args, role) for role in ROLES}
    for role in ROLES:
        value = values[role]
        if value is None:
            value = input(f"{role} provider/model[/effort]: ").strip()
        provider, model, effort = split_selection(value)
        entry = {"provider": provider, "model": model}
        if effort:
            entry["effort"] = effort
        selections[role] = entry
    if dry_run:
        print("[dry run] ZCode team:", json.dumps(selections))
        return
    team.parent.mkdir(parents=True, exist_ok=True)
    team.write_text(json.dumps(selections, indent=2) + "\n", encoding="utf-8")
    print(f"saved ZCode team configuration: {team}")


def configure_codex(args: argparse.Namespace) -> None:
    if args.codex_provider:
        raise ValueError("Codex does not accept provider selection; configure provider in Codex runtime settings")
    if args.codex_model:
        print(f"Codex model: {args.codex_model}")
    if args.codex_effort:
        print(f"Codex effort: {args.codex_effort}")
    if not args.codex_model and not args.non_interactive:
        model = input("Codex model (provider is configured by Codex): ").strip()
        effort = input("Codex effort: ").strip()
        print(f"Codex selection: model={model}, effort={effort}")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        runtime = args.runtime or ask_runtime()
        if args.codex_provider:
            raise ValueError("Codex does not support --codex-provider")
        if runtime in ("zcode", "both"):
            run_install("zcode", args.target, args.force, args.dry_run)
            team = args.team or Path.home() / ".zcode/cli/plugins/local/polyloom/data/team.json"
            if args.non_interactive or args.lead or args.builder or args.runner:
                configure_zcode(args, team, args.dry_run)
        if runtime in ("codex", "both"):
            run_install("codex", args.target, args.force, args.dry_run)
            configure_codex(args)
        print("Validated runtime installation and configuration.")
        print("Setup complete." if not args.dry_run else "Dry run complete.")
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
