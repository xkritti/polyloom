from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from zcode_config import validate_team_config  # noqa: E402


def config() -> dict:
    return {
        "provider": {
            "p": {
                "models": {
                    "lead-model": {"reasoning": {"variants": ["low", "high"]}},
                    "worker-model": {"reasoning": {"variants": ["off"]}},
                }
            }
        }
    }


def test_team_config_requires_the_three_polyloom_roles() -> None:
    team = {"lead": {"provider": "p", "model": "lead-model", "effort": "high"}}
    try:
        validate_team_config(config(), team)
    except ValueError as error:
        assert "builder" in str(error)
    else:
        raise AssertionError("incomplete team must be rejected")


def test_team_config_validates_each_role_against_zcode_models() -> None:
    team = {
        "lead": {"provider": "p", "model": "lead-model", "effort": "high"},
        "builder": {"provider": "p", "model": "worker-model", "effort": "off"},
        "runner": {"provider": "p", "model": "worker-model", "effort": "off"},
    }
    assert validate_team_config(config(), team) is None


def test_team_config_rejects_unknown_role() -> None:
    team = {
        "lead": {"provider": "p", "model": "lead-model", "effort": "high"},
        "builder": {"provider": "p", "model": "worker-model", "effort": "off"},
        "runner": {"provider": "p", "model": "worker-model", "effort": "off"},
        "reviewer": {"provider": "p", "model": "worker-model", "effort": "off"},
    }
    try:
        validate_team_config(config(), team)
    except ValueError as error:
        assert "reviewer" in str(error)
    else:
        raise AssertionError("unknown role must be rejected")
