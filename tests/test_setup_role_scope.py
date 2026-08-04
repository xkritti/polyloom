from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "scripts/setup.py"


def test_setup_has_role_scope_selection():
    text = SETUP.read_text(encoding="utf-8")
    assert "choose_roles_to_configure" in text
    assert "One role" in text
    assert "All roles" in text
    assert "Keep current team" in text


def test_setup_merges_with_existing_team():
    text = SETUP.read_text(encoding="utf-8")
    assert "merged = dict(existing)" in text
    assert "merged.update(selections)" in text


def test_setup_shows_current_role_in_menu():
    text = SETUP.read_text(encoding="utf-8")
    assert "current:" in text


def test_setup_keeps_untouched_roles():
    text = SETUP.read_text(encoding="utf-8")
    assert "merged" in text


def test_setup_returns_empty_when_keep():
    text = SETUP.read_text(encoding="utf-8")
    assert "return []" in text


def test_setup_returns_all_roles_when_no_existing():
    text = SETUP.read_text(encoding="utf-8")
    assert "return list(ROLES)" in text


def test_setup_command_documents_single_role_flow():
    text = (ROOT / "commands/polyloom-setup.md").read_text(encoding="utf-8")
    assert "Reconfigure one role" in text
    assert "Reconfigure all roles" in text
    assert "Keep current team" in text
    assert "Only configure the chosen role" in text
    assert "Leave the other two untouched" in text
