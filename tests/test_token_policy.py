from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def skill() -> str:
    return (ROOT / "skills/polyloom/SKILL.md").read_text(encoding="utf-8")


def command() -> str:
    return (ROOT / "commands/polyloom.md").read_text(encoding="utf-8")


def test_skill_forbids_full_transcript() -> None:
    assert "do not send the full parent transcript" in re.sub(r"\s+", " ", skill().lower())


def test_skill_requires_relevant_context_only() -> None:
    assert "relevant context" in skill()


def test_skill_requires_bounded_worker_report() -> None:
    text = skill()
    for field in ("changed files", "checks", "failures", "risks"):
        assert field in text


def test_command_requires_bounded_worker_report() -> None:
    text = command()
    for field in ("changed files", "checks", "failures", "risks"):
        assert field in text


def test_command_forbids_full_transcript() -> None:
    assert "full parent transcript" in command()


def test_skill_requires_no_spawn_when_not_needed() -> None:
    assert "small fixes where delegation adds no value" in re.sub(r"\s+", " ", skill().lower())
