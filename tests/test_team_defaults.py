from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from zcode_config import default_team_path  # noqa: E402


def test_default_team_path_uses_zcode_plugin_data(tmp_path: Path) -> None:
    assert default_team_path(tmp_path) == tmp_path / "team.json"


def test_default_team_path_is_not_zcode_runtime_config(tmp_path: Path) -> None:
    assert default_team_path(tmp_path) != tmp_path / "config.json"
