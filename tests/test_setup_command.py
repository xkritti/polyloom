from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_setup_command_exists() -> None:
    assert (ROOT / "commands/polyloom-setup.md").exists()


def test_setup_command_has_frontmatter() -> None:
    text = (ROOT / "commands/polyloom-setup.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "description:" in text
    assert "skills: polyloom" in text


def test_setup_command_asks_provider_then_model() -> None:
    text = re.sub(r"\s+", " ", (ROOT / "commands/polyloom-setup.md").read_text(encoding="utf-8"))
    assert "choose a **provider**" in text
    assert "choose a **model**" in text
    assert "Ask one field at a time" in text


def test_setup_command_uses_polyloom_config() -> None:
    text = (ROOT / "commands/polyloom-setup.md").read_text(encoding="utf-8")
    assert "polyloom_config.py" in text


def test_setup_command_shows_summary() -> None:
    text = (ROOT / "commands/polyloom-setup.md").read_text(encoding="utf-8")
    assert "summary" in text.lower()


def test_setup_command_one_question_at_a_time() -> None:
    text = (ROOT / "commands/polyloom-setup.md").read_text(encoding="utf-8")
    assert "Ask one field at a time" in text
    assert text.count("Ask one field at a time") == 1


def test_setup_command_no_credentials() -> None:
    text = (ROOT / "commands/polyloom-setup.md").read_text(encoding="utf-8")
    assert "API keys" in text or "credentials" in text


def test_setup_command_bilingual() -> None:
    text = (ROOT / "commands/polyloom-setup.md").read_text(encoding="utf-8")
    assert "user's language" in text
    assert "Thai or English" in text
