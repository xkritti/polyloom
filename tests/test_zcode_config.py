from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from zcode_config import available_efforts, validate_role_config  # noqa: E402


def test_plugin_manifest_declares_zcode_skills() -> None:
    manifest = json.loads((ROOT / ".zcode-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "polyloom"
    assert manifest["skills"] == "skills"


def test_available_efforts_reads_model_specific_variants() -> None:
    config = {
        "provider": {
            "p": {
                "models": {
                    "reasoning-model": {
                        "reasoning": {"variants": ["low", "max"]}
                    },
                    "plain-model": {},
                }
            }
        }
    }
    assert available_efforts(config, "p", "reasoning-model") == ["low", "max"]
    assert available_efforts(config, "p", "plain-model") == []


def test_validate_role_config_rejects_unsupported_effort() -> None:
    config = {"provider": {"p": {"models": {"m": {"reasoning": {"variants": ["low"]}}}}}}
    try:
        validate_role_config(config, "p", "m", "max")
    except ValueError as error:
        assert "max" in str(error)
    else:
        raise AssertionError("unsupported effort must be rejected")


def test_validate_role_config_accepts_supported_effort() -> None:
    config = {"provider": {"p": {"models": {"m": {"reasoning": {"variants": ["low"]}}}}}}
    assert validate_role_config(config, "p", "m", "low") is None
