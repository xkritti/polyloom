from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "scripts/setup.py"


def test_setup_uses_numbered_runtime_menu() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "1) ZCode" in text
    assert "2) Codex" in text
    assert "3) Both" in text
    assert "select_menu" in text


def test_setup_has_overwrite_menu() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Overwrite" in text
    assert "Keep existing" in text
    assert "Cancel" in text
    assert "confirm_overwrite" in text


def test_setup_keeps_noninteractive_mode() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "--non-interactive" in text
    assert "--force" in text


def test_setup_zcode_role_menu_is_numbered() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Choose provider" in text
    assert "Choose model" in text
    assert "Choose effort" in text
    assert "select_menu" in text


def test_setup_does_not_require_force_in_interactive_mode() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "confirm_overwrite" in text
    assert "--force" in text


def test_setup_menu_has_invalid_choice_handling() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Invalid choice" in text


def test_setup_menu_preserves_runtime_boundary() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Codex provider is configured" in text
    assert "ZCode provider" in text


def test_setup_menu_has_summary() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Summary" in text
    assert "Setup complete" in text


def test_setup_menu_preserves_dry_run() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "--dry-run" in text
    assert "dry run" in text.lower()


def test_setup_menu_does_not_print_credentials() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "credentials" in text.lower()
    assert "apiKey" not in text


def test_setup_menu_preserves_bilingual_prompts() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Thai or English" in text
    assert "user's language" in text


def test_setup_menu_supports_back_and_skip() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "back" in text.lower()
    assert "skip" in text.lower()


def test_setup_menu_keeps_both_runtime() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "both" in text.lower()
    assert "install_zcode" in text
    assert "install_codex" in text


def test_setup_menu_is_single_entrypoint() -> None:
    assert SETUP.exists()
    assert 'if __name__ == "__main__"' in SETUP.read_text(encoding="utf-8")


def test_setup_menu_has_error_handling() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "except" in text
    assert "file=sys.stderr" in text


def test_setup_menu_has_runtime_help() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "--runtime" in text
    assert "--target" in text


def test_setup_menu_has_codex_options() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "--codex-model" in text
    assert "--codex-effort" in text


def test_setup_menu_has_zcode_options() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "--zcode-config" in text
    assert "--team" in text


def test_setup_menu_has_validation() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "validate" in text.lower()
    assert "Validated" in text


def test_setup_menu_preserves_noninteractive_selection_format() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "split_selection" in text
    assert "provider" in text.lower()
    assert "model" in text.lower()
    assert "effort" in text.lower()


def test_setup_menu_uses_no_shell_eval() -> None:
    assert "eval(" not in SETUP.read_text(encoding="utf-8")


def test_setup_menu_documents_overwrite_behavior() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "existing installation" in text.lower()
    assert "--force" in text


def test_setup_menu_has_main_parser() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "ArgumentParser" in text
    assert "parse_args" in text


def test_setup_menu_keeps_team_separate_from_runtime_config() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "team.json" in text
    assert "zcode-config" in text


def test_setup_menu_reports_invalid_runtime() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert 'choices=("zcode", "codex", "both")' in text


def test_setup_menu_has_force_semantics() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "force" in text.lower()
    assert "overwrite" in text.lower()


def test_setup_menu_has_completion_output() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Setup complete" in text
    assert "Dry run complete" in text


def test_setup_menu_has_role_order() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "ROLES = (\"lead\", \"builder\", \"runner\")" in text


def test_setup_menu_has_install_script() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "scripts/install.py" in text


def test_setup_menu_has_no_credential_file_access() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "credentials.json" not in text


def test_setup_menu_has_path_support() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Path" in text


def test_setup_menu_has_subprocess_install() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "subprocess.run" in text


def test_setup_menu_keeps_zcode_and_codex_separate() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "runtime in (\"zcode\", \"both\")" in text
    assert "runtime in (\"codex\", \"both\")" in text


def test_setup_menu_has_summary_function() -> None:
    assert "def print_summary" in SETUP.read_text(encoding="utf-8")


def test_setup_menu_has_configure_functions() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "def configure_zcode" in text
    assert "def configure_codex" in text


def test_setup_menu_has_interactive_role_function() -> None:
    assert "def interactive_zcode_role" in SETUP.read_text(encoding="utf-8")


def test_setup_menu_has_runtime_prompt_function() -> None:
    assert "def ask_runtime" in SETUP.read_text(encoding="utf-8")


def test_setup_menu_has_dry_run_install_behavior() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "dry_run" in text
    assert "[dry run]" in text


def test_setup_menu_has_safe_default_targets() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert ".zcode" in text
    assert ".codex" in text


def test_setup_menu_has_no_provider_for_codex() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Codex does not accept provider selection" in text


def test_setup_menu_is_python3() -> None:
    assert SETUP.read_text(encoding="utf-8").startswith("#!/usr/bin/env python3")


def test_setup_menu_has_force_passthrough() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "command.append(\"--force\")" in text


def test_setup_menu_has_target_passthrough() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert 'command += ["--target", str(target)]' in text


def test_setup_menu_has_team_write() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "team.write_text" in text


def test_setup_menu_has_json_config() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "json.dumps" in text


def test_setup_menu_has_model_catalog_hint() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "polyloom_config.py list" in text


def test_setup_menu_has_setup_wizard_docstring() -> None:
    assert "Interactive Polyloom installer" in SETUP.read_text(encoding="utf-8")


def test_setup_menu_has_no_api_key_output() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "api_key" not in text.lower()


def test_setup_menu_has_runtime_choices_help() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Install Polyloom and configure ZCode or Codex" in text


def test_setup_menu_has_role_selection() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "values = {role: getattr(args, role) for role in ROLES}" in text


def test_setup_menu_has_provider_model_effort_entry() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert 'entry = {"provider": provider, "model": model}' in text


def test_setup_menu_has_codex_summary() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Codex model:" in text
    assert "Codex effort:" in text


def test_setup_menu_has_zcode_summary() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "ZCode team:" in text


def test_setup_menu_has_error_exit() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "return 1" in text


def test_setup_menu_has_success_exit() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "return 0" in text


def test_setup_menu_does_not_use_eval() -> None:
    assert "eval(" not in SETUP.read_text(encoding="utf-8")


def test_setup_menu_has_selection_parser() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "def split_selection" in text


def test_setup_menu_has_runtime_selector() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "def ask_runtime" in text


def test_setup_menu_has_overwrite_selector() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "def confirm_overwrite" in text


def test_setup_menu_has_numbered_choices() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "1) ZCode" in text
    assert "2) Codex" in text
    assert "3) Both" in text


def test_setup_menu_has_invalid_choice_message() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Invalid choice" in text


def test_setup_menu_has_keep_existing_message() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Keep existing" in text


def test_setup_menu_has_cancel_message() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Cancel" in text


def test_setup_menu_has_overwrite_message() -> None:
    text = SETUP.read_text(encoding="utf-8")
    assert "Overwrite" in text
