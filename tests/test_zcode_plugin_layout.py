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


def test_skill_declares_role_names_and_luna_max() -> None:
    skill = (ROOT / "skills/polyloom/SKILL.md").read_text()
    assert all(role in skill for role in ("orchestrator", "dev", "runner", "qa", "git-manager", "plane-manager"))
    assert "gpt-5.6-sol" in skill
    assert "gpt-5.6-terra" in skill
    assert "gpt-5.6-luna" in skill
    assert "max" in skill
