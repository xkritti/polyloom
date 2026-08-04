#!/usr/bin/env python3
"""Install Polyloom plugin into ZCode plugin directory."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "polyloom"

# Files that must exist in the source bundle
BUNDLE = [
    ".zcode-plugin/plugin.json",
    "commands/polyloom.md",
    "commands/polyloom-setup.md",
    "skills/polyloom/SKILL.md",
    "scripts/polyloom_config.py",
    "scripts/zcode_config.py",
    "scripts/validate.py",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Install Polyloom into ZCode plugin directory.")
    p.add_argument(
        "--target",
        type=Path,
        default=None,
        help="Destination directory (default: auto-detect ZCode user plugins).",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing installation.",
    )
    return p.parse_args()


def default_target() -> Path:
    home = Path.home()
    candidates = [
        home / ".zcode" / "cli" / "plugins" / "local",
        home / ".zcode" / "plugins",
    ]
    for c in candidates:
        if c.parent.exists():
            return c
    return candidates[0]


def validate_bundle() -> None:
    missing = [f for f in BUNDLE if not (REPO_ROOT / f).exists()]
    if missing:
        raise FileNotFoundError(f"missing bundle files: {missing}")


def install(target: Path, force: bool = False) -> None:
    validate_bundle()
    dest = target / PLUGIN_NAME
    if dest.exists() and not force:
        raise FileExistsError(f"refusing overwrite: {dest} (use --force)")
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for item in BUNDLE:
        src = REPO_ROOT / item
        dst = dest / item
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    print(f"installed polyloom -> {dest}")


def main() -> int:
    args = parse_args()
    target = args.target or default_target()
    try:
        install(target, force=args.force)
    except (FileExistsError, FileNotFoundError) as e:
        print(str(e), flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
