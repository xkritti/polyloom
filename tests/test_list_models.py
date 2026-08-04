from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from zcode_config import list_models  # noqa: E402


def test_list_models_returns_provider_model_effort() -> None:
    config = {
        "provider": {
            "p1": {
                "enabled": True,
                "models": {
                    "model-a": {"reasoning": {"variants": ["low", "high"]}},
                },
            },
        }
    }
    models = list_models(config)
    assert len(models) == 1
    entry = models[0]
    assert entry["provider"] == "p1"
    assert entry["model"] == "model-a"
    assert entry["efforts"] == ["low", "high"]


def test_list_models_excludes_disabled_providers() -> None:
    config = {
        "provider": {
            "p1": {"enabled": True, "models": {"m": {}}},
            "p2": {"enabled": False, "models": {"m": {}}},
        }
    }
    models = list_models(config)
    assert all(m["provider"] != "p2" for m in models)


def test_list_models_handles_no_reasoning() -> None:
    config = {"provider": {"p": {"enabled": True, "models": {"m": {}}}}}
    models = list_models(config)
    assert models[0]["efforts"] == []


def test_list_models_does_not_expose_credentials() -> None:
    config = {
        "provider": {
            "p": {
                "enabled": True,
                "apiKey": "sk-SECRET",
                "models": {"m": {"reasoning": {"variants": ["low"]}}},
            },
        }
    }
    models = list_models(config)
    for entry in models:
        assert "apiKey" not in entry
        assert "SECRET" not in str(entry)


def test_list_models_defaults_enabled_when_field_absent() -> None:
    config = {"provider": {"p": {"models": {"m": {}}}}}
    models = list_models(config)
    assert len(models) == 1


def test_list_models_includes_default_variant() -> None:
    config = {
        "provider": {
            "p": {
                "enabled": True,
                "models": {
                    "m": {"reasoning": {"variants": ["low", "high"], "defaultVariant": "low"}},
                },
            },
        }
    }
    models = list_models(config)
    assert models[0].get("default_effort") == "low"


def test_list_models_excludes_system_disabled() -> None:
    config = {
        "provider": {
            "p": {"enabled": True, "models": {"m": {}}},
            "q": {"systemDisabledReason": "oauth", "models": {"m": {}}},
        }
    }
    models = list_models(config)
    assert all(m["provider"] != "q" for m in models)
