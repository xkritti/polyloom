import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_declares_commands_and_skills() -> None:
    manifest = json.loads((ROOT / ".zcode-plugin/plugin.json").read_text())
    assert manifest["skills"] == "skills"
    assert manifest["commands"] == "commands"


def test_command_loads_polyloom_skill() -> None:
    command = (ROOT / "commands/polyloom.md").read_text()
    assert "skills: polyloom" in command
    assert "$ARGUMENTS" in command


def test_skill_declares_role_names_without_upstream_model_names() -> None:
    skill = (ROOT / "skills/polyloom/SKILL.md").read_text()
    assert "builder" in skill
    assert "runner" in skill
    assert "gpt-5.6-sol" not in skill
    assert "gpt-5.6-terra" not in skill
    assert "gpt-5.6-luna" not in skill
