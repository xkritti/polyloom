#!/usr/bin/env python3
"""Install Polyloom project-local Codex and Claude adapters safely by default.

ZCode: registers the plugin in the marketplace + installed records and copies
plugin files into the plugin cache, exactly as ZCode's GUI install does.
Without --force, ZCode refreshes bundled files in place and preserves extra
cache files. --force replaces the cache directory, removing stale extras.
Codex: copies skill + agent files into the Codex home.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import shutil
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "polyloom"
PLUGIN_VERSION = "0.1.0"
MARKETPLACE_ID = "polyloom-local"
PLUGIN_ID = f"{PLUGIN_NAME}@{MARKETPLACE_ID}"

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

PROJECT_AGENTS = [".agents/AGENTS.md"] + [f".agents/{name}.md" for name in ("orchestrator", "dev", "runner", "qa", "git-manager", "plane-manager")]
PROJECT_CODEX = [".codex/config.toml"]
PROJECT_CLAUDE = [".claude/CLAUDE.md"] + [f".claude/agents/{name}.md" for name in ("orchestrator", "dev", "runner", "qa", "git-manager", "plane-manager")]


def parse_args() -> argparse.Namespace:
    raw_args = sys.argv[1:]
    p = argparse.ArgumentParser(description="Install Polyloom project adapters (Codex+Claude by default) or legacy ZCode/Codex user assets.")
    p.add_argument("--target", type=Path, default=None, help="Codex destination directory (default: auto-detect).")
    p.add_argument("--runtime", choices=("zcode", "codex", "claude", "both"), default="both", help="Which runtime to install for (default: both project adapters).")
    p.add_argument("--scope", choices=("user", "project"), default="project", help="Install scope (default: project; never writes global homes).")
    p.add_argument("--project-root", type=Path, default=None, help="Project root for --scope project (default: current directory).")
    p.add_argument("--dry-run", action="store_true", help="Print project plan without writing files.")
    p.add_argument("--uninstall", action="store_true", help="Remove only manifest-owned project files.")
    p.add_argument("--force", action="store_true", help="Replace existing installation; ZCode removes stale cache files.")
    p.add_argument("--zcode-home", type=Path, default=None, help="ZCode config root (default: ~/.zcode). For tests.")
    args = p.parse_args()
    args.scope_explicit = any(arg == "--scope" or arg.startswith("--scope=") for arg in raw_args)
    return args


def default_zcode_home() -> Path:
    return Path.home() / ".zcode"


def default_target(runtime: str, zcode_home: Path | None = None) -> Path:
    if runtime == "codex":
        return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    return (zcode_home or default_zcode_home()) / "cli" / "plugins"


def validate_bundle(bundle: list[str]) -> None:
    missing = [f for f in bundle if not (REPO_ROOT / f).exists()]
    if missing:
        raise FileNotFoundError(f"missing bundle files: {missing}")


def _validate_manifest(data: dict) -> tuple[list[str], dict[str, str]]:
    files = data.get("files", [])
    hashes = data.get("hashes", {})
    if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
        raise ValueError("manifest files must be a list of relative paths")
    if not isinstance(hashes, dict) or not all(
        isinstance(item, str) and isinstance(value, str) for item, value in hashes.items()
    ):
        raise ValueError("manifest hashes must be an object of string values")
    if len(files) != len(set(files)):
        raise ValueError("manifest files must not contain duplicates")
    if set(hashes) != set(files):
        raise ValueError("manifest must contain one hash for every owned file")
    for item in files:
        path = Path(item)
        if not item or path.is_absolute() or ".." in path.parts:
            raise ValueError(f"manifest path must be relative and contained: {item!r}")
        if re.fullmatch(r"[0-9a-f]{64}", hashes[item]) is None:
            raise ValueError(f"manifest hash is invalid for: {item}")
    return files, hashes


def install_project(root: Path, runtime: str, force: bool = False, dry_run: bool = False) -> None:
    if runtime not in ("codex", "claude", "both"):
        raise ValueError("project scope supports runtime codex, claude, or both")
    root = root.resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"project root must be an existing directory: {root}")
    def safe(item: str) -> Path:
        path = (root / item).resolve()
        if path != root and root not in path.parents:
            raise ValueError(f"manifest path escapes project root: {item}")
        return path
    bundles = {".agents": PROJECT_AGENTS}
    if runtime in ("codex", "both"): bundles[".codex"] = PROJECT_CODEX
    if runtime in ("claude", "both"): bundles[".claude"] = PROJECT_CLAUDE
    files = [item for bundle in bundles.values() for item in bundle]
    for bundle in bundles.values(): validate_bundle(bundle)
    manifest_path = root / ".polyloom-install.json"
    owned: set[str] = set()
    data: dict = {}
    if manifest_path.exists():
        data = _read_json(manifest_path, {})
        manifest_files, prior_hashes = _validate_manifest(data)
        owned = set(manifest_files)
    else:
        prior_hashes = {}
    for item in files: safe(item)
    for item in owned: safe(item)
    conflicts = [item for item in files if safe(item).exists() and item not in owned]
    if conflicts:
        raise FileExistsError(f"refusing overwrite of unowned files (force cannot override ownership): {conflicts}")
    modified = []
    for item in files:
        destination = safe(item)
        if item not in owned or not destination.exists():
            continue
        if not destination.is_file() or hashlib.sha256(destination.read_bytes()).hexdigest() != prior_hashes[item]:
            modified.append(item)
    if modified:
        raise FileExistsError(f"refusing overwrite of user-modified owned files: {modified}")
    print(f"project install ({runtime}) -> {root}")
    if dry_run:
        for item in files: print(f"[dry run] {item}")
        return
    for item in files:
        destination = safe(item)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / item, destination)
    runtimes = set(data.get("runtimes", [])) if manifest_path.exists() else set()
    runtimes.update(("codex", "claude") if runtime == "both" else (runtime,))
    all_files = sorted(owned | set(files))
    hashes = dict(prior_hashes)
    hashes.update({item: hashlib.sha256((root / item).read_bytes()).hexdigest() for item in files if (root / item).is_file()})
    _write_json(manifest_path, {"version": 1, "runtimes": sorted(runtimes), "files": all_files, "hashes": hashes})


def uninstall_project(root: Path, dry_run: bool = False) -> None:
    manifest_path = root.resolve() / ".polyloom-install.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"project manifest not found: {manifest_path}")
    data = _read_json(manifest_path, {})
    files, hashes = _validate_manifest(data)
    root = root.resolve()
    remaining = []
    remaining_hashes = {}
    for item in files:
        path = (root / item).resolve()
        if path != root and root not in path.parents:
            raise ValueError(f"manifest path escapes project root: {item}")
        if not path.exists():
            continue
        if hashes and hashes.get(item) != hashlib.sha256(path.read_bytes()).hexdigest():
            print(f"preserve modified owned file: {item}")
            remaining.append(item)
            remaining_hashes[item] = hashes.get(item)
            continue
        if dry_run:
            print(f"[dry run] remove {item}")
        elif path.is_file():
            path.unlink()
    if not dry_run:
        if remaining:
            _write_json(manifest_path, {"version": 1, "runtimes": data.get("runtimes", []), "files": remaining, "hashes": remaining_hashes})
        else:
            manifest_path.unlink()
    print(f"project uninstall -> {root.resolve()}")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _read_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in {path}") from error
    if not isinstance(data, dict):
        raise ValueError(f"JSON object required in {path}")
    return data


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
        temporary = Path(handle.name)
    try:
        temporary.replace(path)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def _upsert_marketplace(km_path: Path) -> None:
    km = _read_json(km_path, {"version": 1, "marketplaces": []})
    if not isinstance(km.get("marketplaces"), list):
        raise ValueError(f"marketplaces must be a list in {km_path}")
    entry = next(
        (m for m in km["marketplaces"] if isinstance(m, dict) and m.get("id") == MARKETPLACE_ID),
        None,
    )
    now = _now()
    if entry is None:
        entry = {
            "id": MARKETPLACE_ID,
            "source": {"source": "directory", "path": str(REPO_ROOT)},
            "name": MARKETPLACE_ID,
            "description": "Polyloom multi-agent software team for ZCode.",
            "addedAt": now,
            "lastUpdated": now,
            "pluginCount": 1,
        }
        km["marketplaces"].append(entry)
    else:
        source = {"source": "directory", "path": str(REPO_ROOT)}
        if entry.get("source") != source or entry.get("pluginCount") != 1:
            entry["source"] = source
            entry["pluginCount"] = 1
            entry["lastUpdated"] = now
    _write_json(km_path, km)


def _upsert_installed(ip_path: Path, install_path: Path) -> None:
    ip = _read_json(ip_path, {"version": 1, "plugins": []})
    if not isinstance(ip.get("plugins"), list):
        raise ValueError(f"plugins must be a list in {ip_path}")
    entry = next(
        (p for p in ip["plugins"] if isinstance(p, dict) and p.get("id") == PLUGIN_ID),
        None,
    )
    expected = {
        "id": PLUGIN_ID,
        "name": PLUGIN_NAME,
        "marketplace": MARKETPLACE_ID,
        "version": PLUGIN_VERSION,
        "installPath": str(install_path),
        "scope": "user",
        "source": "./",
    }
    if entry is None:
        now = _now()
        entry = {**expected, "installedAt": now, "updatedAt": now}
        ip["plugins"].append(entry)
    elif any(entry.get(key) != value for key, value in expected.items()):
        entry.update(expected)
        entry["updatedAt"] = _now()
    _write_json(ip_path, ip)


def _enable_plugin(config_path: Path) -> None:
    cfg = _read_json(config_path, {"plugins": {"enabledPlugins": {}}})
    plugins = cfg.setdefault("plugins", {})
    if not isinstance(plugins, dict):
        raise ValueError(f"plugins must be an object in {config_path}")
    enabled = plugins.setdefault("enabledPlugins", {})
    if not isinstance(enabled, dict):
        raise ValueError(f"enabledPlugins must be an object in {config_path}")
    enabled[PLUGIN_ID] = True
    _write_json(config_path, cfg)


def _validate_zcode_metadata(plugins: Path, config_path: Path) -> None:
    marketplace = _read_json(plugins / "known_marketplaces.json", {"version": 1, "marketplaces": []})
    if not isinstance(marketplace.get("marketplaces"), list):
        raise ValueError(f"marketplaces must be a list in {plugins / 'known_marketplaces.json'}")
    installed = _read_json(plugins / "installed_plugins.json", {"version": 1, "plugins": []})
    if not isinstance(installed.get("plugins"), list):
        raise ValueError(f"plugins must be a list in {plugins / 'installed_plugins.json'}")
    config = _read_json(config_path, {"plugins": {"enabledPlugins": {}}})
    if "plugins" in config and not isinstance(config["plugins"], dict):
        raise ValueError(f"plugins must be an object in {config_path}")
    enabled = config.get("plugins", {}).get("enabledPlugins")
    if enabled is not None and not isinstance(enabled, dict):
        raise ValueError(f"enabledPlugins must be an object in {config_path}")


def install_zcode(zcode_home: Path, force: bool) -> None:
    validate_bundle(ZCODE_BUNDLE)
    plugins = zcode_home / "cli" / "plugins"
    install_path = plugins / "cache" / MARKETPLACE_ID / PLUGIN_NAME / PLUGIN_VERSION
    config_path = zcode_home / "cli" / "config.json"

    _validate_zcode_metadata(plugins, config_path)

    if install_path.exists() and force:
        shutil.rmtree(install_path)
    install_path.mkdir(parents=True, exist_ok=True)
    for item in ZCODE_BUNDLE:
        dst = install_path / item
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / item, dst)

    _upsert_marketplace(plugins / "known_marketplaces.json")
    _upsert_installed(plugins / "installed_plugins.json", install_path)
    _enable_plugin(config_path)

    print(f"installed polyloom (zcode) -> {install_path}")


def install_codex(target: Path, force: bool) -> None:
    validate_bundle(CODEX_BUNDLE)
    skills_dest = target / "skills" / PLUGIN_NAME
    agents_dest = target / "agents"

    existing: list[Path] = []
    for p in [skills_dest, agents_dest / "lead.toml", agents_dest / "builder-worker.toml", agents_dest / "runner-worker.toml"]:
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
    try:
        # A destination flag is the legacy user-install API; retain compatibility
        # for callers that predate the project-scope default.
        if args.scope == "project" and not args.scope_explicit and (args.target is not None or args.zcode_home is not None) and args.project_root is None:
            args.scope = "user"
        if args.scope == "project":
            if args.target is not None or args.zcode_home is not None:
                raise ValueError("project scope uses --project-root, not --target or --zcode-home")
            if args.uninstall:
                uninstall_project(args.project_root or Path.cwd(), dry_run=args.dry_run)
            else:
                install_project(args.project_root or Path.cwd(), args.runtime, force=args.force, dry_run=args.dry_run)
            return 0
        if args.uninstall:
            raise ValueError("--uninstall is supported only with --scope project")
        if args.project_root is not None:
            raise ValueError("--project-root is supported only with --scope project")
        if args.dry_run or args.runtime in ("claude", "both"):
            raise ValueError("claude and dry-run are supported only with --scope project")
        if args.runtime == "zcode":
            if args.target is not None:
                raise ValueError("--target is only supported for codex; use --zcode-home for ZCode")
            zhome = args.zcode_home or default_zcode_home()
            install_zcode(zhome, force=args.force)
        else:
            target = args.target or default_target("codex")
            install_codex(target, force=args.force)
    except (FileExistsError, FileNotFoundError, ValueError) as e:
        print(str(e), flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
