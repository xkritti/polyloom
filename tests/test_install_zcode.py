from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts/install.py"
PY = sys.executable


def test_installer_zcode_copies_plugin_to_target(tmp_path: Path) -> None:
    target = tmp_path / "plugins"
    result = subprocess.run(
        [PY, str(INSTALLER), "--runtime", "zcode", "--target", str(target)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    dest = target / "polyloom"
    assert (dest / ".zcode-plugin/plugin.json").exists()
    assert (dest / "commands/polyloom.md").exists()
    assert (dest / "commands/polyloom-setup.md").exists()
    assert (dest / "skills/polyloom/SKILL.md").exists()
    assert (dest / "scripts/polyloom_config.py").exists()
    assert (dest / "scripts/zcode_config.py").exists()


def test_installer_codex_copies_skill_and_agents(tmp_path: Path) -> None:
    target = tmp_path / "codex-home"
    result = subprocess.run(
        [PY, str(INSTALLER), "--runtime", "codex", "--target", str(target)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (target / "skills/polyloom/SKILL.md").exists()
    assert (target / "agents/lead.toml").exists()
    assert (target / "agents/builder-worker.toml").exists()
    assert (target / "agents/runner-worker.toml").exists()


def test_installer_zcode_refuses_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "plugins"
    subprocess.run([PY, str(INSTALLER), "--runtime", "zcode", "--target", str(target)], capture_output=True)
    result = subprocess.run(
        [PY, str(INSTALLER), "--runtime", "zcode", "--target", str(target)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "refusing overwrite" in result.stdout


def test_installer_codex_refuses_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "codex-home"
    subprocess.run([PY, str(INSTALLER), "--runtime", "codex", "--target", str(target)], capture_output=True)
    result = subprocess.run(
        [PY, str(INSTALLER), "--runtime", "codex", "--target", str(target)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "refusing overwrite" in result.stdout


def test_installer_force_overwrites_zcode(tmp_path: Path) -> None:
    target = tmp_path / "plugins"
    subprocess.run([PY, str(INSTALLER), "--runtime", "zcode", "--target", str(target)], capture_output=True)
    result = subprocess.run(
        [PY, str(INSTALLER), "--runtime", "zcode", "--target", str(target), "--force"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr


def test_installer_force_overwrites_codex(tmp_path: Path) -> None:
    target = tmp_path / "codex-home"
    subprocess.run([PY, str(INSTALLER), "--runtime", "codex", "--target", str(target)], capture_output=True)
    result = subprocess.run(
        [PY, str(INSTALLER), "--runtime", "codex", "--target", str(target), "--force"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr


def test_installer_does_not_touch_zcode_config(tmp_path: Path) -> None:
    fake_zcode = tmp_path / "fake-zcode"
    fake_zcode.mkdir()
    (fake_zcode / "config.json").write_text('{"should":"not_touch"}')
    target = tmp_path / "plugins"
    subprocess.run([PY, str(INSTALLER), "--runtime", "zcode", "--target", str(target)], capture_output=True)
    assert (fake_zcode / "config.json").read_text() == '{"should":"not_touch"}'


def test_codex_agents_have_no_upstream_model_names() -> None:
    builder = (ROOT / "agents/builder-worker.toml").read_text()
    runner = (ROOT / "agents/runner-worker.toml").read_text()
    # model defaults are OK but must not hardcode Solweaver-specific names as immutable
    assert "team.json" in builder
    assert "team.json" in runner
    assert "Polyloom" in builder
    assert "Polyloom" in runner


def test_codex_agents_report_bounded_evidence() -> None:
    builder = (ROOT / "agents/builder-worker.toml").read_text()
    runner = (ROOT / "agents/runner-worker.toml").read_text()
    for text in (builder, runner):
        assert "changed files" in text
        assert "checks" in text
        assert "failures" in text
        assert "risks" in text
