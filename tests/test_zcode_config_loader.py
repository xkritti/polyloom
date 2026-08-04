from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from zcode_config import load_zcode_config, load_team_config  # noqa: E402


def test_load_zcode_config_reads_provider_model_registry(tmp_path: Path) -> None:
    source = tmp_path / "config.json"
    source.write_text('{"provider": {"p": {"models": {"m": {}}}}}')
    assert load_zcode_config(source)["provider"]["p"]["models"]["m"] == {}


def test_load_team_config_returns_validated_roles(tmp_path: Path) -> None:
    source = tmp_path / "team.json"
    source.write_text(
        '{"lead":{"provider":"p","model":"m"},'
        '"builder":{"provider":"p","model":"m"},'
        '"runner":{"provider":"p","model":"m"}}'
    )
    zcode = {"provider": {"p": {"models": {"m": {}}}}}
    assert set(load_team_config(source, zcode)) == {"lead", "builder", "runner"}


def test_load_team_config_rejects_malformed_json(tmp_path: Path) -> None:
    source = tmp_path / "team.json"
    source.write_text("not json")
    try:
        load_team_config(source, {})
    except ValueError as error:
        assert "JSON" in str(error)
    else:
        raise AssertionError("malformed team config must be rejected")


def test_load_team_config_rejects_missing_file(tmp_path: Path) -> None:
    try:
        load_team_config(tmp_path / "missing.json", {})
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("missing team config must be rejected")
