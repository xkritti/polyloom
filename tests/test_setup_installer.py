from pathlib import Path
import subprocess
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "scripts/setup.py"
INSTALL_SH = ROOT / "install.sh"
PY = sys.executable


def test_setup_help_lists_modes_and_options():
    result = subprocess.run([PY, str(SETUP), "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    for value in ("zcode", "codex", "both", "--interactive", "--dry-run", "--force"):
        assert value in result.stdout


def test_install_sh_delegates_to_setup():
    text = INSTALL_SH.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env bash")
    assert "scripts/setup.py" in text
    assert "exec" in text


def test_setup_noninteractive_codex(tmp_path: Path):
    result = subprocess.run(
        [PY, str(SETUP), "--runtime", "codex", "--non-interactive", "--target", str(tmp_path),
         "--codex-model", "gpt-test", "--codex-effort", "high"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "skills/polyloom/SKILL.md").exists()
    assert (tmp_path / "agents/orchestrator.toml").exists()
    for name in ("orchestrator.toml", "dev.toml", "runner.toml", "qa.toml", "git-manager.toml", "plane-manager.toml"):
        agent = (tmp_path / "agents" / name).read_text()
        assert re.search(r'^model = "gpt-test"$', agent, re.MULTILINE)
        assert re.search(r'^model_reasoning_effort = "high"$', agent, re.MULTILINE)


def test_setup_can_update_only_the_codex_effort(tmp_path: Path):
    result = subprocess.run(
        [PY, str(SETUP), "--runtime", "codex", "--non-interactive", "--target", str(tmp_path),
         "--codex-effort", "low"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    agent = (tmp_path / "agents" / "orchestrator.toml").read_text()
    assert re.search(r'^model = "gpt-5.6-sol"$', agent, re.MULTILINE)
    assert re.search(r'^model_reasoning_effort = "low"$', agent, re.MULTILINE)


def test_setup_dry_run_does_not_write(tmp_path: Path):
    result = subprocess.run(
        [PY, str(SETUP), "--runtime", "codex", "--non-interactive", "--dry-run", "--target", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert not (tmp_path / "skills").exists()
    assert not (tmp_path / "agents").exists()


def test_setup_rejects_provider_for_codex(tmp_path: Path):
    result = subprocess.run(
        [PY, str(SETUP), "--runtime", "codex", "--non-interactive", "--target", str(tmp_path),
         "--codex-provider", "bad"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "provider" in result.stderr.lower()


def test_setup_rejects_codex_options_for_zcode(tmp_path: Path):
    result = subprocess.run(
        [PY, str(SETUP), "--runtime", "zcode", "--non-interactive", "--target", str(tmp_path),
         "--codex-model", "gpt-test"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "Codex runtime" in result.stderr


def test_setup_source_documents_runtime_boundary():
    text = SETUP.read_text(encoding="utf-8")
    assert "provider, then model, then effort" in text
    assert "Codex" in text
    assert "credentials" in text.lower()
    assert "validate" in text.lower()


def test_setup_codex_defaults_are_not_provider_fields():
    text = SETUP.read_text(encoding="utf-8")
    assert "--codex-model" in text
    assert "--codex-effort" in text
    assert "--codex-provider" in text


def test_setup_supports_both_runtime():
    result = subprocess.run([PY, str(SETUP), "--help"], capture_output=True, text=True)
    assert "both" in result.stdout


def test_setup_source_has_interactive_prompts():
    text = SETUP.read_text(encoding="utf-8")
    assert "input(" in text
    assert "provider" in text.lower()
    assert "model" in text.lower()
    assert "effort" in text.lower()
