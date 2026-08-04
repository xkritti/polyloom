from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts/install.py"
PY = sys.executable


def test_installer_copies_plugin_to_target(tmp_path: Path) -> None:
    target = tmp_path / "plugins"
    result = subprocess.run(
        [PY, str(INSTALLER), "--target", str(target)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    dest = target / "polyloom"
    assert (dest / ".zcode-plugin/plugin.json").exists()
    assert (dest / "commands/polyloom.md").exists()
    assert (dest / "skills/polyloom/SKILL.md").exists()
    assert (dest / "scripts/polyloom_config.py").exists()
    assert (dest / "scripts/zcode_config.py").exists()


def test_installer_refuses_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "plugins"
    subprocess.run([PY, str(INSTALLER), "--target", str(target)], capture_output=True)
    result = subprocess.run(
        [PY, str(INSTALLER), "--target", str(target)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "refusing overwrite" in result.stdout


def test_installer_force_overwrites(tmp_path: Path) -> None:
    target = tmp_path / "plugins"
    subprocess.run([PY, str(INSTALLER), "--target", str(target)], capture_output=True)
    result = subprocess.run(
        [PY, str(INSTALLER), "--target", str(target), "--force"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr


def test_installer_does_not_touch_zcode_config(tmp_path: Path) -> None:
    fake_zcode = tmp_path / "fake-zcode"
    fake_zcode.mkdir()
    (fake_zcode / "config.json").write_text('{"should":"not_touch"}')
    target = tmp_path / "plugins"
    subprocess.run(
        [PY, str(INSTALLER), "--target", str(target)],
        capture_output=True,
    )
    assert (fake_zcode / "config.json").read_text() == '{"should":"not_touch"}'
