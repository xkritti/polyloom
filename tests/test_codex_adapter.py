from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts/install.py"
PY = sys.executable
AGENTS = ("lead.toml", "builder-worker.toml", "runner-worker.toml")
PROJECT_ROLES = ("orchestrator", "dev", "runner", "qa", "git-manager", "plane-manager")


def agent_text(name: str) -> str:
    return (ROOT / "agents" / name).read_text(encoding="utf-8")


def test_codex_agents_exist_and_have_runtime_fields() -> None:
    for name in AGENTS:
        text = agent_text(name)
        assert 'model = "' in text
        assert 'model_reasoning_effort = "' in text
        assert "provider =" not in text


def test_codex_lead_is_read_only() -> None:
    text = agent_text("lead.toml").lower()
    assert "read-only" in text
    assert "never modify repository files" in text
    assert "review" in text


def test_codex_workers_report_bounded_evidence() -> None:
    for name in AGENTS:
        text = agent_text(name)
        for field in ("changed files", "checks", "failures", "risks"):
            assert field in text


def test_project_skill_documents_luna_max_roles() -> None:
    text = (ROOT / "skills/polyloom/SKILL.md").read_text(encoding="utf-8")
    assert "Codex" in text
    assert "gpt-5.6-luna" in text
    assert "max" in text


def test_project_agents_are_native_luna_max_custom_agents() -> None:
    for role in PROJECT_ROLES:
        text = (ROOT / ".codex/agents" / f"{role}.toml").read_text(encoding="utf-8")
        assert f'name = "{role}"' in text
        assert 'model = "gpt-5.6-luna"' in text
        assert 'model_reasoning_effort = "max"' in text
        assert 'developer_instructions = """' in text


def test_setup_command_is_zcode_only() -> None:
    text = (ROOT / "commands/polyloom-setup.md").read_text(encoding="utf-8")
    assert "ZCode-only" in text
    assert "Codex provider" in text


def test_installer_codex_copies_skill_and_all_agents(tmp_path: Path) -> None:
    target = tmp_path / "codex-home"
    result = subprocess.run(
        [PY, str(INSTALLER), "--runtime", "codex", "--target", str(target)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (target / "skills/polyloom/SKILL.md").exists()
    for name in AGENTS:
        assert (target / "agents" / name).exists()


def test_installer_codex_omits_zcode_files(tmp_path: Path) -> None:
    target = tmp_path / "codex-home"
    subprocess.run(
        [PY, str(INSTALLER), "--runtime", "codex", "--target", str(target)],
        check=True,
    )
    assert not (target / ".zcode-plugin").exists()
    assert not (target / "commands").exists()


def test_installer_codex_refuses_overwrite_without_force(tmp_path: Path) -> None:
    target = tmp_path / "codex-home"
    command = [PY, str(INSTALLER), "--runtime", "codex", "--target", str(target)]
    subprocess.run(command, check=True, capture_output=True)
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 1
    assert "refusing overwrite" in result.stdout


def test_installer_codex_force_overwrites(tmp_path: Path) -> None:
    target = tmp_path / "codex-home"
    command = [PY, str(INSTALLER), "--runtime", "codex", "--target", str(target)]
    subprocess.run(command, check=True, capture_output=True)
    result = subprocess.run(command + ["--force"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_installer_declares_separate_runtime_paths() -> None:
    text = (ROOT / "scripts/install.py").read_text(encoding="utf-8")
    assert "install_codex" in text
    assert "install_zcode" in text
    assert 'choices=("zcode", "codex", "claude", "both")' in text
    assert 'choices=("user", "project")' in text
    assert "install_project" in text
    assert "CODEX_HOME" in text
