from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "scripts/setup.py"


def test_interactive_mode_configures_zcode_after_install():
    text = SETUP.read_text(encoding="utf-8")
    assert "if not args.non_interactive" in text
    assert "configure_zcode(args, team, args.dry_run)" in text


def test_interactive_mode_does_not_finish_without_team_setup():
    text = SETUP.read_text(encoding="utf-8")
    assert "if args.non_interactive or args.lead or args.builder or args.runner" not in text


def test_interactive_mode_configures_codex_after_install():
    text = SETUP.read_text(encoding="utf-8")
    assert "configure_codex(args)" in text


def test_zcode_setup_has_three_role_prompts():
    text = SETUP.read_text(encoding="utf-8")
    assert "for role in ROLES" in text
    for role in ("lead", "builder", "runner"):
        assert role in text


def test_setup_completion_requires_configuration_flow():
    text = SETUP.read_text(encoding="utf-8")
    assert "saved ZCode team configuration" in text
    assert "Setup complete" in text
