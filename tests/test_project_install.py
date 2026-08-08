import json
from pathlib import Path

import pytest
import subprocess
import sys

from scripts.install import install_project, uninstall_project, parse_args


def test_project_codex_claude_merge_and_manifest(tmp_path: Path):
    install_project(tmp_path, "codex")
    install_project(tmp_path, "claude")
    manifest = json.loads((tmp_path / ".polyloom-install.json").read_text())
    assert manifest["runtimes"] == ["claude", "codex"]
    assert (tmp_path / ".agents/AGENTS.md").exists()
    assert (tmp_path / ".codex/config.toml").exists()
    assert (tmp_path / ".claude/CLAUDE.md").exists()


def test_project_both_records_concrete_runtimes(tmp_path: Path):
    install_project(tmp_path, "both")
    manifest = json.loads((tmp_path / ".polyloom-install.json").read_text())
    assert manifest["runtimes"] == ["claude", "codex"]


def test_installer_defaults_are_safe_project_both(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["install.py"])
    args = parse_args()
    assert args.scope == "project"
    assert args.runtime == "both"


def test_dry_run_does_not_write(tmp_path: Path):
    install_project(tmp_path, "codex", dry_run=True)
    assert not (tmp_path / ".polyloom-install.json").exists()


def test_unowned_conflict_even_force(tmp_path: Path):
    path = tmp_path / ".agents/AGENTS.md"
    path.parent.mkdir()
    path.write_text("user")
    with pytest.raises(FileExistsError):
        install_project(tmp_path, "codex", force=True)


def test_modified_owned_file_preserved_on_update_and_uninstall(tmp_path: Path):
    install_project(tmp_path, "codex")
    config = tmp_path / ".codex/config.toml"
    config.write_text("user edit")
    with pytest.raises(FileExistsError):
        install_project(tmp_path, "codex")
    uninstall_project(tmp_path)
    assert config.exists()


def test_uninstall_removes_unchanged(tmp_path: Path):
    install_project(tmp_path, "claude")
    uninstall_project(tmp_path)
    assert not (tmp_path / ".polyloom-install.json").exists()
    assert not (tmp_path / ".claude/CLAUDE.md").exists()


def test_direct_imm_layout(tmp_path: Path):
    install_project(tmp_path, "both")
    roles = ("orchestrator", "dev", "runner", "qa", "git-manager", "plane-manager")
    assert all((tmp_path / ".agents" / f"{r}.md").exists() for r in roles)
    assert all((tmp_path / ".claude/agents" / f"{r}.md").exists() for r in roles)
    assert (tmp_path / ".codex/config.toml").read_text().find('../.agents/AGENTS.md') >= 0
    assert not (tmp_path / ".agents/roles").exists()
    assert not (tmp_path / ".codex/agents").exists()


def test_modified_owned_manifest_retained_and_force_rejected(tmp_path: Path):
    install_project(tmp_path, "codex")
    config = tmp_path / ".codex/config.toml"
    config.write_text("modified")
    with pytest.raises(FileExistsError):
        install_project(tmp_path, "codex", force=True)
    uninstall_project(tmp_path)
    assert config.exists() and (tmp_path / ".polyloom-install.json").exists()


def test_manifest_traversal_rejected(tmp_path: Path):
    (tmp_path / ".polyloom-install.json").write_text(
        json.dumps({"files": ["../escape"], "hashes": {"../escape": "0" * 64}})
    )
    with pytest.raises(ValueError):
        uninstall_project(tmp_path)


def test_manifest_requires_hash_for_every_owned_file(tmp_path: Path):
    victim = tmp_path / "important.txt"
    victim.write_text("keep")
    (tmp_path / ".polyloom-install.json").write_text(
        json.dumps({"files": ["important.txt"], "hashes": {}})
    )
    with pytest.raises(ValueError):
        install_project(tmp_path, "codex")
    with pytest.raises(ValueError):
        uninstall_project(tmp_path)
    assert victim.read_text() == "keep"


def test_malformed_manifest_returns_value_error(tmp_path: Path):
    (tmp_path / ".polyloom-install.json").write_text(
        json.dumps({"files": [[]], "hashes": {}})
    )
    with pytest.raises(ValueError):
        uninstall_project(tmp_path)


def test_project_cli_runtime_and_dry_run(tmp_path: Path):
    installer = Path(__file__).parents[1] / "scripts/install.py"
    run = lambda *args: subprocess.run([sys.executable, str(installer), *args], cwd=tmp_path, capture_output=True, text=True)
    assert run("--scope", "project", "--project-root", str(tmp_path), "--runtime", "both", "--dry-run").returncode == 0
    assert not (tmp_path / ".polyloom-install.json").exists()
    assert run("--scope", "project", "--project-root", str(tmp_path), "--runtime", "zcode").returncode != 0


def test_cli_rejects_conflicting_project_and_user_options(tmp_path: Path):
    installer = Path(__file__).parents[1] / "scripts/install.py"
    run = lambda *args: subprocess.run([sys.executable, str(installer), *args], cwd=tmp_path, capture_output=True, text=True)
    target = tmp_path / "legacy-target"
    project_target = run("--scope", "project", "--runtime", "codex", "--target", str(target))
    assert project_target.returncode != 0
    assert not (target / "skills/polyloom/SKILL.md").exists()
    user_uninstall = run("--scope", "user", "--runtime", "codex", "--target", str(target), "--uninstall")
    assert user_uninstall.returncode != 0
    assert not (target / "skills/polyloom/SKILL.md").exists()
