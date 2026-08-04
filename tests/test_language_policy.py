from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def skill() -> str:
    return (ROOT / "skills/polyloom/SKILL.md").read_text(encoding="utf-8")


def test_skill_declares_bilingual_output() -> None:
    text = skill()
    assert "Thai or English" in text
    assert "user's language" in text


def test_skill_preserves_technical_identifiers() -> None:
    assert "technical identifiers" in skill()


def test_skill_does_not_duplicate_translations() -> None:
    text = skill()
    assert "แปล" not in text
    assert "translate" not in text.lower()


def test_skill_keeps_code_paths_commands_unchanged() -> None:
    text = skill()
    assert "file paths" in text
    assert "commands" in text
    assert "error messages" in text
