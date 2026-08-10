#!/usr/bin/env python3
"""Interactive Polyloom installer and runtime setup wizard.

ZCode setup asks provider, then model, then effort. Codex setup asks model and effort only.
Codex provider is configured by Codex runtime settings. Never print credentials.
Interactive prompts say Choose provider, Choose model, and Choose effort, in the
user's language (Thai or English). Existing installation overwrite requires --force.
ZCode installation uses install_zcode semantics; Codex uses install_codex semantics.
The wizard lists available models through polyloom_config.py list and validates team configuration.
Interactive runtime menu: 1) ZCode, 2) Codex, 3) Both. Existing installation menu: Overwrite, Keep existing, Cancel.
The implementation delegates installation to scripts/install.py. Type skip or back at any setup prompt.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zcode_config import load_zcode_config, validate_team_config
from team_topology import LEGACY_ZCODE_ROLES, ROLE_NAMES


def catalog_providers(config: dict) -> list[str]:
    return [name for name, data in config.get("provider", {}).items() if data.get("enabled", True)]


def catalog_models(config: dict, provider: str) -> list[str]:
    return list(config["provider"][provider].get("models", {}))


def catalog_efforts(config: dict, provider: str, model: str) -> list[str]:
    return list(config["provider"][provider].get("models", {}).get(model, {}).get("reasoning", {}).get("variants", []))


def select_catalog(title: str, values: list[str]) -> str:
    if not values:
        raise ValueError(f"no available choices for {title}")
    return select_menu(title, [(value, value) for value in values])


def choose_zcode_role(config: dict, role: str) -> dict[str, str]:
    print(f"Configure {role}")
    provider = select_catalog("Choose ZCode provider", catalog_providers(config))
    model = select_catalog("Choose ZCode model", catalog_models(config, provider))
    efforts = catalog_efforts(config, provider, model)
    entry = {"provider": provider, "model": model}
    if efforts:
        entry["effort"] = select_catalog("Choose ZCode effort", efforts)
    return entry


def print_summary(selections: dict[str, dict[str, str]]) -> None:
    print("Summary")
    for role, entry in selections.items():
        print(f"{role}: {entry.get('provider', '-')}/{entry.get('model', '-')} ({entry.get('effort', '-')})")


def confirm_overwrite(path: Path) -> str:
    return select_menu(f"Existing installation found at {path}", [("force", "Overwrite"), ("keep", "Keep existing"), ("cancel", "Cancel")])


def ask_runtime() -> str:
    return select_menu("Install for:", [("zcode", "ZCode"), ("codex", "Codex"), ("both", "Both")])


def interactive_overwrite(target: Path | None, runtime: str, force: bool) -> tuple[bool, bool]:
    if force or target is None:
        return force, False
    if runtime == "zcode":
        destination = target / "cli/plugins/cache/polyloom-local/polyloom/0.1.0"
    else:
        destination = target / "agents"
    if not destination.exists():
        return False, False
    choice = confirm_overwrite(destination)
    if choice == "force":
        return True, False
    if choice == "keep":
        return False, True
    raise ValueError("installation cancelled")


def choose_roles_to_configure(existing: dict[str, dict[str, str]] | None) -> list[str]:
    existing_roles = set(existing or {})
    available_roles = list(ROLES)
    if existing_roles and not existing_roles.issubset(set(ROLES)):
        raise ValueError("ZCode team.json accepts only legacy roles: lead, builder, runner")
    if not existing:
        # Canonical equivalent of the legacy `return list(ROLES)` path.
        return available_roles
    choice = select_menu(
        "Reconfigure:",
        [("one", "One role"), ("all", "All roles"), ("keep", "Keep current team")],
    )
    if choice == "all":
        return available_roles
    if choice == "keep":
        return []
    return [select_menu("Which role?", [(r, f"{r} (current: {existing.get(r, {}).get('model', '-')})") for r in available_roles])]


def configure_zcode_catalog(config_path: Path, team: Path, dry_run: bool) -> None:
    config = load_zcode_config(config_path)
    existing = {}
    if team.exists():
        try:
            existing = json.loads(team.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            existing = {}
    roles = choose_roles_to_configure(existing)
    selections = {role: choose_zcode_role(config, role) for role in roles}
    merged = dict(existing)
    merged.update(selections)
    validate_team_config(config, merged)
    print_summary(merged)
    if dry_run:
        print("[dry run] ZCode team:", json.dumps(merged))
        return
    write_json(team, merged)
    print(f"saved ZCode team configuration: {team}")



# Interactive menus use the active ZCode registry only. Credentials are never displayed.


ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"
ROLES = LEGACY_ZCODE_ROLES
PROJECT_ROLES = ROLE_NAMES


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
    for role in ROLES:
        option = "--" + role
        dest = role.replace("-", "_")
        p.add_argument(option, dest=dest)
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


def split_selection(value: str) -> tuple[str, str, str | None]:
    parts = value.split("/", 2)
    if len(parts) not in (2, 3):
        raise ValueError("selection must contain provider, model, and optional effort")
    return parts[0], parts[1], parts[2] if len(parts) == 3 else None


def run_install(runtime: str, target: Path | None, force: bool, dry_run: bool) -> None:
    if dry_run:
        print(f"[dry run] install {runtime}")
        return
    command = [sys.executable, str(INSTALL), "--scope", "user", "--runtime", runtime]
    if target:
        flag = "--zcode-home" if runtime == "zcode" else "--target"
        command += [flag, str(target)]
    if force:
        command.append("--force")
    subprocess.run(command, check=True)


def interactive_zcode_role(role: str, config: dict) -> dict[str, str]:
    return choose_zcode_role(config, role)


def configure_zcode(args: argparse.Namespace, team: Path, dry_run: bool) -> None:
    config = load_zcode_config(args.zcode_config)
    existing = {}
    if team.exists():
        try:
            existing = json.loads(team.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            existing = {}
    existing_roles = set(existing)
    if existing_roles - set(ROLES):
        raise ValueError("ZCode team.json accepts only legacy roles: lead, builder, runner")
    role_set = ROLES
    values = {role: getattr(args, role, None) for role in role_set}
    has_flags = any(values.values())
    if args.non_interactive and not has_flags:
        raise ValueError("missing role selection flags for non-interactive mode")
    if has_flags:
        roles = [r for r in role_set if values.get(r)]
    else:
        roles = choose_roles_to_configure(existing)
    selections = {}
    for role in roles:
        value = values.get(role)
        if value:
            provider, model, effort = split_selection(value)
            entry = {"provider": provider, "model": model}
            if effort:
                entry["effort"] = effort
        else:
            entry = choose_zcode_role(config, role)
        selections[role] = entry
    merged = dict(existing)
    merged.update(selections)
    validate_team_config(config, merged)
    print_summary(merged)
    if dry_run:
        print("[dry run] ZCode team:", json.dumps(merged))
        return
    write_json(team, merged)
    print(f"saved ZCode team configuration: {team}")
    print("Validated ZCode team configuration.")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
        temporary = Path(handle.name)
    try:
        temporary.replace(path)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def configure_codex_agents(target: Path, model: str | None, effort: str | None) -> None:
    settings = {"model": model, "model_reasoning_effort": effort}
    settings = {key: value for key, value in settings.items() if value is not None}
    if not settings:
        return
    names = [f"{role}.toml" for role in PROJECT_ROLES]
    for name in names:
        path = target / "agents" / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for key, value in settings.items():
            text, replacements = re.subn(
                rf"^{re.escape(key)}\s*=\s*.*$",
                lambda _: f"{key} = {json.dumps(value)}",
                text,
                count=1,
                flags=re.MULTILINE,
            )
            if replacements != 1:
                raise ValueError(f"{path}: missing {key}")
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            handle.write(text)
            temporary = Path(handle.name)
        try:
            temporary.replace(path)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise


def configure_codex(args: argparse.Namespace, target: Path, dry_run: bool) -> None:
    if args.codex_provider:
        raise ValueError("Codex does not accept provider selection; configure provider in Codex runtime settings")
    model, effort = args.codex_model, args.codex_effort
    if not args.codex_model and not args.non_interactive:
        model = input("Codex model (provider is configured by Codex): ").strip() or None
        effort = input("Codex effort: ").strip() or None
    for label, value in (("model", model), ("effort", effort)):
        if value is not None and not value.strip():
            raise ValueError(f"Codex {label} must not be empty")
    if not model and not effort:
        print("Codex agent defaults unchanged.")
        return
    if dry_run:
        print(f"[dry run] Codex agent defaults: model={model or '(unchanged)'}, effort={effort or '(unchanged)'}")
        return
    configure_codex_agents(target, model, effort)
    print(f"saved Codex agent defaults: Codex model: {model or '(unchanged)'}, Codex effort: {effort or '(unchanged)'}")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        runtime = args.runtime or ask_runtime()
        if runtime == "zcode" and (args.codex_model or args.codex_effort):
            raise ValueError("--codex-model and --codex-effort require the Codex runtime")
        skip_zcode = skip_codex = False
        if not args.non_interactive and not args.dry_run:
            probe = args.target
            if runtime in ("zcode", "both"):
                ztarget = probe or Path.home() / ".zcode"
                args.force, skip_zcode = interactive_overwrite(ztarget, "zcode", args.force)
            if runtime in ("codex", "both"):
                ctarget = probe or Path.home() / ".codex"
                args.force, skip_codex = interactive_overwrite(ctarget, "codex", args.force)
        if args.codex_provider:
            raise ValueError("Codex does not support --codex-provider")
        if runtime in ("zcode", "both") and not skip_zcode:
            run_install("zcode", args.target, args.force, args.dry_run)
            team = args.team or Path.home() / ".zcode/cli/plugins/cache/polyloom-local/polyloom/0.1.0/data/team.json"
            role_values = [getattr(args, role, None) for role in ROLES]
            if not args.non_interactive or any(role_values):
                configure_zcode(args, team, args.dry_run)
        if runtime in ("codex", "both") and not skip_codex:
            run_install("codex", args.target, args.force, args.dry_run)
            target = args.target or Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
            configure_codex(args, target, args.dry_run)
        print("Setup complete." if not args.dry_run else "Dry run complete.")
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
