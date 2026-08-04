#!/usr/bin/env python3
"""Install Polyloom plugin into ZCode or Codex."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "polyloom"

ZCODE_BUNDLE = [
    ".zcode-plugin/plugin.json",
    "commands/polyloom.md",
    "commands/polyloom-setup.md",
    "skills/polyloom/SKILL.md",
    "scripts/polyloom_config.py",
    "scripts/zcode_config.py",
    "scripts/validate.py",
]

CODEX_BUNDLE = [
    "skills/polyloom/SKILL.md",
    "agents/lead.toml",
    "agents/builder-worker.toml",
    "agents/runner-worker.toml",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Install Polyloom into ZCode or Codex.")
    p.add_argument(
        "--target",
        type=Path,
        default=None,
        help="Destination directory (default: auto-detect).",
    )
    p.add_argument(
        "--runtime",
        choices=("zcode", "codex"),
        default="zcode",
        help="Which runtime to install for (default: zcode).",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing installation.",
    )
    return p.parse_args()


def default_target(runtime: str) -> Path:
    home = Path.home()
    if runtime == "codex":
        return Path(os.environ.get("CODEX_HOME", home / ".codex"))
    candidates = [
        home / ".zcode" / "cli" / "plugins" / "local",
        home / ".zcode" / "plugins",
    ]
    for c in candidates:
        if c.parent.exists():
            return c
    return candidates[0]


def validate_bundle(bundle: list[str]) -> None:
    missing = [f for f in bundle if not (REPO_ROOT / f).exists()]
    if missing:
        raise FileNotFoundError(f"missing bundle files: {missing}")


def install_zcode(target: Path, force: bool) -> None:
    validate_bundle(ZCODE_BUNDLE)
    dest = target / PLUGIN_NAME
    if dest.exists() and not force:
        raise FileExistsError(f"refusing overwrite: {dest} (use --force)")
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for item in ZCODE_BUNDLE:
        src = REPO_ROOT / item
        dst = dest / item
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    print(f"installed polyloom (zcode) -> {dest}")


def install_codex(target: Path, force: bool) -> None:
    validate_bundle(CODEX_BUNDLE)
    skills_dest = target / "skills" / PLUGIN_NAME
    agents_dest = target / "agents"

    existing: list[Path] = []
    for p in [skills_dest, agents_dest / "builder-worker.toml", agents_dest / "runner-worker.toml"]:
        if p.exists():
            existing.append(p)
    if existing and not force:
        raise FileExistsError(f"refusing overwrite: {existing} (use --force)")

    if skills_dest.exists():
        shutil.rmtree(skills_dest)
    skills_dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO_ROOT / "skills/polyloom/SKILL.md", skills_dest / "SKILL.md")

    agents_dest.mkdir(parents=True, exist_ok=True)
    for name in ("lead.toml", "builder-worker.toml", "runner-worker.toml"):
        shutil.copy2(REPO_ROOT / "agents" / name, agents_dest / name)

    print(f"installed polyloom (codex) -> {target}")


def main() -> int:
    args = parse_args()
    target = args.target or default_target(args.runtime)
    try:
        if args.runtime == "zcode":
            install_zcode(target, force=args.force)
        else:
            install_codex(target, force=args.force)
    except (FileExistsError, FileNotFoundError) as e:
        print(str(e), flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
