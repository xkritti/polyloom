from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from zcode_config import load_zcode_config  # noqa: E402
from setup import catalog_providers, catalog_models, catalog_efforts  # noqa: E402


def config():
    return load_zcode_config(ROOT / "tests/fixtures/zcode-config.json")


def test_provider_catalog_contains_only_enabled_providers():
    providers = catalog_providers(config())
    assert providers == ["p"]


def test_model_catalog_is_scoped_to_provider():
    assert catalog_models(config(), "p") == ["m", "plain"]


def test_effort_catalog_is_scoped_to_model():
    assert catalog_efforts(config(), "p", "m") == ["low", "high"]
    assert catalog_efforts(config(), "p", "plain") == []


def test_setup_source_uses_numbered_catalog_menus():
    text = (ROOT / "scripts/setup.py").read_text(encoding="utf-8")
    assert "catalog_providers" in text
    assert "catalog_models" in text
    assert "catalog_efforts" in text
    assert "select_menu" in text


def test_setup_source_does_not_print_credentials():
    text = (ROOT / "scripts/setup.py").read_text(encoding="utf-8")
    assert "apiKey" not in text
    assert "credentials.json" not in text
