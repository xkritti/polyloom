import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "polyloom_config.py"
PY = sys.executable


def make_config(path: Path) -> None:
    path.write_text(json.dumps({
        "provider": {
            "p": {
                "enabled": True,
                "models": {
                    "m": {"reasoning": {"variants": ["low", "high"]}},
                    "plain": {},
                },
            },
            "disabled-p": {"enabled": False, "models": {"m": {}}},
        }
    }))


def run_cli(zcode: Path, team: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PY, str(CLI), *args, "--zcode-config", str(zcode), "--team", str(team)],
        capture_output=True, text=True,
    )


def test_set_lead_persists(tmp_path: Path) -> None:
    zc, team = tmp_path / "z.json", tmp_path / "t.json"
    make_config(zc)
    result = run_cli(zc, team, "set", "lead", "p", "m", "high")
    assert result.returncode == 0, result.stderr
    data = json.loads(team.read_text())
    assert data["lead"] == {"provider": "p", "model": "m", "effort": "high"}


def test_set_rejects_invalid_effort(tmp_path: Path) -> None:
    zc, team = tmp_path / "z.json", tmp_path / "t.json"
    make_config(zc)
    result = run_cli(zc, team, "set", "lead", "p", "m", "max")
    assert result.returncode != 0
    assert not team.exists()


def test_set_rejects_unknown_role(tmp_path: Path) -> None:
    zc, team = tmp_path / "z.json", tmp_path / "t.json"
    make_config(zc)
    result = run_cli(zc, team, "set", "reviewer", "p", "m")
    assert result.returncode != 0


def test_set_preserves_other_roles(tmp_path: Path) -> None:
    zc, team = tmp_path / "z.json", tmp_path / "t.json"
    make_config(zc)
    run_cli(zc, team, "set", "lead", "p", "m", "low")
    run_cli(zc, team, "set", "builder", "p", "m", "high")
    data = json.loads(team.read_text())
    assert data["lead"]["effort"] == "low"
    assert data["builder"]["effort"] == "high"


def test_set_plain_model_no_effort(tmp_path: Path) -> None:
    zc, team = tmp_path / "z.json", tmp_path / "t.json"
    make_config(zc)
    result = run_cli(zc, team, "set", "lead", "p", "plain")
    assert result.returncode == 0
    data = json.loads(team.read_text())
    assert "effort" not in data["lead"]


def test_validate_requires_all_three_roles(tmp_path: Path) -> None:
    zc, team = tmp_path / "z.json", tmp_path / "t.json"
    make_config(zc)
    team.write_text(json.dumps({"lead": {"provider": "p", "model": "m", "effort": "low"}}))
    result = run_cli(zc, team, "validate")
    assert result.returncode != 0
    assert "builder" in result.stderr


def test_show_displays_roles(tmp_path: Path) -> None:
    zc, team = tmp_path / "z.json", tmp_path / "t.json"
    make_config(zc)
    team.write_text(json.dumps({
        "lead": {"provider": "p", "model": "m", "effort": "low"},
        "builder": {"provider": "p", "model": "m"},
        "runner": {"provider": "p", "model": "plain"},
    }))
    result = run_cli(zc, team, "show")
    assert result.returncode == 0
    assert "lead: p/m" in result.stdout
    assert "builder: p/m" in result.stdout


def test_list_shows_models_no_credentials(tmp_path: Path) -> None:
    zc, team = tmp_path / "z.json", tmp_path / "t.json"
    make_config(zc)
    result = run_cli(zc, team, "list")
    assert result.returncode == 0
    assert "p/m" in result.stdout
    assert "apiKey" not in result.stdout
    assert "disabled-p" not in result.stdout


def test_reset_deletes_team(tmp_path: Path) -> None:
    zc, team = tmp_path / "z.json", tmp_path / "t.json"
    make_config(zc)
    team.write_text("{}")
    result = run_cli(zc, team, "reset")
    assert result.returncode == 0
    assert not team.exists()


def test_set_rejects_disabled_provider(tmp_path: Path) -> None:
    zc, team = tmp_path / "z.json", tmp_path / "t.json"
    make_config(zc)
    result = run_cli(zc, team, "set", "lead", "disabled-p", "m")
    assert result.returncode != 0
