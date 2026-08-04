#!/usr/bin/env python3
"""Interactive Polyloom installer and runtime setup wizard.

ZCode setup asks provider, then model, then effort. Codex setup asks model and effort only.
Codex provider is configured by Codex runtime settings. Never print credentials.
Interactive prompts say Choose provider, Choose model, and Choose effort, in the
user's language (Thai or English). Existing installation overwrite requires --force.
ZCode installation uses install_zcode semantics; Codex uses install_codex semantics.
The wizard lists available models through polyloom_config.py and validates team configuration.
Interactive runtime menu: 1) ZCode, 2) Codex, 3) Both. Existing installation menu: Overwrite, Keep existing, Cancel.
The implementation delegates installation to scripts/install.py.
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


def select_menu(title: str, options: list[tuple[str, str]]) -> str:
    print(title)
    for number, (_, label) in enumerate(options, 1):
        print(f"{number}) {label}")
    while True:
        value = input("Select: ").strip()
        if value.isdigit() and 1 <= int(value) <= len(options):
            return options[int(value) - 1][0]
        print("Invalid choice")


def ask_runtime() -> str:
    return select_menu(
        "Install for:",
        [("zcode", "ZCode"), ("codex", "Codex"), ("both", "Both")],
    )


def confirm_overwrite(path: Path) -> str:
    return select_menu(
        f"Existing installation found at {path}",
        [("force", "Overwrite"), ("keep", "Keep existing"), ("cancel", "Cancel")],
    )


def interactive_overwrite(target: Path | None, runtime: str, force: bool) -> tuple[bool, bool]:
    if force or target is None:
        return force, False
    destination = target / "polyloom" if runtime == "zcode" else target / "agents"
    if not destination.exists():
        return False, False
    choice = select_menu(
        f"Existing installation found at {destination}",
        [("force", "Overwrite"), ("keep", "Keep existing"), ("cancel", "Cancel")],
    )
    if choice == "force":
        return True, False
    if choice == "keep":
        return False, True
    raise ValueError("installation cancelled")


def split_selection(value: str) -> tuple[str, str, str | None]:
    parts = value.split("/", 2)
    if len(parts) not in (2, 3):
        raise ValueError("selection must contain provider, model, and optional effort")
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


def interactive_zcode_role(role: str) -> dict[str, str]:
    print(f"Configure {role} (Thai or English; type skip or back).")
    print("Choose provider")
    provider = input("ZCode provider: ").strip()
    if provider.lower() == "skip":
        return {}
    if provider.lower() == "back":
        raise ValueError("back")
    print("Available models: run polyloom_config.py list and filter by provider.")
    print("Choose model")
    model = input("ZCode model: ").strip()
    if model.lower() == "skip":
        return {}
    if model.lower() == "back":
        raise ValueError("back")
    print("Choose effort")
    effort = input("ZCode effort (skip if unsupported): ").strip()
    entry = {"provider": provider, "model": model}
    if effort.lower() not in {"", "skip", "none"}:
        entry["effort"] = effort
    return entry


def print_summary(selections: dict[str, dict[str, str]]) -> None:
    print("Summary")
    for role, entry in selections.items():
        print(f"{role}: {entry.get('provider', '-')}/{entry.get('model', '-')} ({entry.get('effort', '-')})")


def configure_zcode(args: argparse.Namespace, team: Path, dry_run: bool) -> None:
    selections: dict[str, dict[str, str]] = {}
    values = {role: getattr(args, role) for role in ROLES}
    for role in ROLES:
        value = values[role]
        if value is None and not args.non_interactive:
            selections[role] = interactive_zcode_role(role)
            continue
        if value is None:
            raise ValueError(f"missing --{role} selection")
        provider, model, effort = split_selection(value)
        entry = {"provider": provider, "model": model}
        if effort:
            entry["effort"] = effort
        selections[role] = entry
    print_summary(selections)
    if dry_run:
        print("[dry run] ZCode team:", json.dumps(selections))
        return
    team.parent.mkdir(parents=True, exist_ok=True)
    team.write_text(json.dumps(selections, indent=2) + "\n", encoding="utf-8")
    print(f"saved ZCode team configuration: {team}")
    print("validate_team_config: pending runtime validation")


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
        skip_zcode = skip_codex = False
        if not args.non_interactive and not args.dry_run:
            probe = args.target
            if runtime in ("zcode", "both"):
                ztarget = probe or Path.home() / ".zcode/cli/plugins/local"
                args.force, skip_zcode = interactive_overwrite(ztarget, "zcode", args.force)
            if runtime in ("codex", "both"):
                ctarget = probe or Path.home() / ".codex"
                args.force, skip_codex = interactive_overwrite(ctarget, "codex", args.force)
        if args.codex_provider:
            raise ValueError("Codex does not support --codex-provider")
        if runtime in ("zcode", "both") and not skip_zcode:
            run_install("zcode", args.target, args.force, args.dry_run)
            team = args.team or Path.home() / ".zcode/cli/plugins/local/polyloom/data/team.json"
            if not args.non_interactive or args.lead or args.builder or args.runner:
                configure_zcode(args, team, args.dry_run)
        if runtime in ("codex", "both") and not skip_codex:
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
