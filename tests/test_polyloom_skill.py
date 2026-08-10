from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def skill() -> str:
    return (ROOT / "skills/polyloom/SKILL.md").read_text(encoding="utf-8")


def test_six_role_contract_and_orchestrator_is_read_only() -> None:
    text = skill()
    assert "name: polyloom" in text
    assert all(role in text for role in ("orchestrator", "dev", "runner", "qa", "git-manager", "plane-manager"))
    assert "coordination-only" in text
    assert "independently verifies" in text


def test_skill_declares_luna_max_without_legacy_worker_names() -> None:
    text = skill()
    assert "gpt-5.6-luna" in text
    assert "max" in text
    for value in ("gpt-5.6-sol", "gpt-5.6-terra", "terra_worker", "luna_worker"):
        assert value not in text
    assert "security_reviewer" not in text
    assert "code_mapper" not in text
    assert "tester" not in text


def test_failed_work_returns_to_same_worker() -> None:
    text = skill()
    assert "same responsible worker" in text
    assert "parent may not fix" in text


def test_model_effort_and_language_policy() -> None:
    text = skill()
    assert "provider" in text and "model" in text and "effort" in text
    assert "Thai or English" in text
    assert "technical identifiers" in text


def test_token_and_evidence_policy() -> None:
    text = skill()
    assert "full parent transcript" in text
    assert "relevant context" in text
    for field in ("changed files", "checks", "failures", "risks"):
        assert field in text
    assert "worker summary is not proof" in text


def test_safe_parallelism_and_verification() -> None:
    text = skill()
    assert "write scopes are disjoint" in text
    assert "Run focused, then risk-appropriate broad checks" in text
    assert "Do not deploy" in text
    assert "user authorized" in text


def test_command_preserves_six_roles() -> None:
    command = (ROOT / "commands/polyloom.md").read_text(encoding="utf-8")
    assert "skills: polyloom" in command
    assert "$ARGUMENTS" in command
    assert "QA independently reviews" in command
    assert "Luna Max" in command
    assert "team configuration" in command
    assert "model alias" in command
    assert "coordination-only" in command
    assert "overlapping write scopes" in command
    assert "same responsible worker" in command
    assert "user authorized" in command


def test_plugin_manifest_bundles_skill_and_command() -> None:
    import json
    manifest = json.loads((ROOT / ".zcode-plugin/plugin.json").read_text())
    assert manifest["name"] == "polyloom"
    assert manifest["skills"] == "skills"
    assert manifest["commands"] == "commands"
    assert (ROOT / "skills/polyloom/SKILL.md").exists()
    assert (ROOT / "commands/polyloom.md").exists()


def test_skill_is_concise() -> None:
    assert len(skill().splitlines()) < 100
    assert len(skill()) < 5000
