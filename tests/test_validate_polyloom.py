from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate  # noqa: E402


def test_validator_uses_polyloom_skill_and_does_not_require_codex_models() -> None:
    assert validate.SKILL_NAME == "polyloom"
    assert validate.validate_polyloom is not None


def test_polyloom_validation_accepts_zcode_plugin() -> None:
    validate.validate_polyloom()
