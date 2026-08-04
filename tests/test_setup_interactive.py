from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "scripts/setup.py"


def test_interactive_zcode_asks_provider_model_effort_separately() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "ZCode provider" in text
    assert "ZCode model" in text
    assert "ZCode effort" in text
    assert "provider/model[/effort]" not in text


def test_interactive_zcode_shows_provider_then_model() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Choose provider" in text
    assert "Choose model" in text
    assert "Choose effort" in text


def test_interactive_zcode_uses_model_catalog() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "polyloom_config.py" in text
    assert "list" in text


def test_noninteractive_still_accepts_provider_model_effort() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "provider/model[/effort]" in text or "split_selection" in text


def test_codex_remains_model_effort_only() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Codex model" in text
    assert "Codex effort" in text
    assert "Codex provider is configured" in text
    assert "Codex provider" in text


def test_interactive_setup_has_back_and_skip() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "skip" in text.lower()
    assert "back" in text.lower()


def test_interactive_setup_prints_summary() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Summary" in text or "summary" in text
    assert "print_summary" in text


def test_interactive_setup_validates_team() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "validate" in text.lower()
    assert "validate_team_config" in text


def test_interactive_setup_never_prints_credentials() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "credentials" in text.lower()
    assert "apiKey" not in text


def test_interactive_setup_is_bilingual() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Thai or English" in text
    assert "user's language" in text


def test_interactive_setup_uses_role_order() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "lead" in text
    assert "builder" in text
    assert "runner" in text
    assert "ROLES" in text


def test_interactive_setup_uses_separate_runtime_paths() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "install_zcode" in text
    assert "install_codex" in text
    assert "both" in text


def test_interactive_setup_has_confirmation_boundary() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "force" in text.lower()
    assert "overwrite" in text.lower()


def test_interactive_setup_keeps_zcode_config_separate() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "team" in text.lower()
    assert "zcode-config" in text


def test_interactive_setup_reports_completion() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Setup complete" in text
    assert "Validated" in text


def test_interactive_setup_has_error_handling() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "except" in text
    assert "file=sys.stderr" in text


def test_interactive_setup_has_main_entrypoint() -> None:
    assert 'if __name__ == "__main__"' in SETUP.read_text(encoding="utf-8")


def test_interactive_setup_does_not_use_shell_eval() -> None:
    assert "eval(" not in SETUP.read_text(encoding="utf-8")


def test_interactive_setup_keeps_technical_identifiers() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "provider" in text.lower()
    assert "model" in text.lower()
    assert "effort" in text.lower()
