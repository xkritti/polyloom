"""ZCode compatibility must stay three-role and isolated from project adapters."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import setup  # noqa: E402
from zcode_config import validate_team_config  # noqa: E402
from install import install_project  # noqa: E402


def zcode_config(path: Path) -> None:
    path.write_text(json.dumps({
        "provider": {"p": {"enabled": True, "models": {"m": {}}}},
    }))


def test_fresh_zcode_setup_writes_legacy_three_roles(tmp_path: Path) -> None:
    config = tmp_path / "zcode.json"
    team = tmp_path / "team.json"
    zcode_config(config)
    args = setup.parser().parse_args([
        "--runtime", "zcode", "--non-interactive",
        "--zcode-config", str(config), "--team", str(team),
        "--lead", "p/m", "--builder", "p/m", "--runner", "p/m",
    ])
    setup.configure_zcode(args, team, dry_run=False)
    assert set(json.loads(team.read_text())) == {"lead", "builder", "runner"}


def test_zcode_validator_rejects_project_role_set(tmp_path: Path) -> None:
    config = {"provider": {"p": {"models": {"m": {}}}}}
    project_team = {role: {"provider": "p", "model": "m"} for role in (
        "orchestrator", "dev", "runner", "qa", "git-manager", "plane-manager"
    )}
    try:
        validate_team_config(config, project_team)
    except ValueError as error:
        assert "unknown roles" in str(error)
    else:
        raise AssertionError("project roles must not enter ZCode team.json")


def test_project_install_remains_exact_six_roles(tmp_path: Path) -> None:
    install_project(tmp_path, "codex")
    roles = {path.stem for path in (tmp_path / ".codex/agents").glob("*.toml")}
    assert roles == {"orchestrator", "dev", "runner", "qa", "git-manager", "plane-manager"}
