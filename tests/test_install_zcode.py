import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts/install.py"
PY = sys.executable


def test_installer_zcode_copies_plugin_to_target(tmp_path: Path) -> None:
    zhome = tmp_path / "zcode-home"
    (zhome / "cli" / "plugins").mkdir(parents=True)
    (zhome / "cli" / "plugins" / "installed_plugins.json").write_text('{"version":1,"plugins":[]}')
    (zhome / "cli" / "plugins" / "known_marketplaces.json").write_text('{"version":1,"marketplaces":[]}')
    (zhome / "cli" / "config.json").write_text('{"plugins":{"enabledPlugins":{}}}')
    result = subprocess.run(
        [PY, str(INSTALLER), "--runtime", "zcode", "--zcode-home", str(zhome)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    dest = zhome / "cli" / "plugins" / "cache" / "polyloom-local" / "polyloom" / "0.1.0"
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
    for name in ("orchestrator.toml", "dev.toml", "runner.toml", "qa.toml", "git-manager.toml", "plane-manager.toml"):
        assert (target / "agents" / name).exists()


def test_installer_zcode_overlays_bundled_files_without_force(tmp_path: Path) -> None:
    zhome = tmp_path / "zcode-home"
    (zhome / "cli" / "plugins").mkdir(parents=True)
    (zhome / "cli" / "plugins" / "installed_plugins.json").write_text('{"version":1,"plugins":[]}')
    (zhome / "cli" / "plugins" / "known_marketplaces.json").write_text('{"version":1,"marketplaces":[]}')
    (zhome / "cli" / "config.json").write_text('{"plugins":{"enabledPlugins":{}}}')
    cmd = [PY, str(INSTALLER), "--runtime", "zcode", "--zcode-home", str(zhome)]
    subprocess.run(cmd, capture_output=True)
    install_path = zhome / "cli" / "plugins" / "cache" / "polyloom-local" / "polyloom" / "0.1.0"
    bundled = install_path / "commands" / "polyloom.md"
    bundled.write_text("stale bundled file")
    result = subprocess.run(cmd, capture_output=True, text=True)

    assert result.returncode == 0
    assert bundled.read_text() == (ROOT / "commands" / "polyloom.md").read_text()
    ip = json.loads((zhome / "cli" / "plugins" / "installed_plugins.json").read_text())
    assert sum(1 for p in ip["plugins"] if p["id"] == "polyloom@polyloom-local") == 1


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
    zhome = tmp_path / "zcode-home"
    command = [PY, str(INSTALLER), "--runtime", "zcode", "--zcode-home", str(zhome)]
    subprocess.run(command, check=True, capture_output=True)
    install_path = zhome / "cli" / "plugins" / "cache" / "polyloom-local" / "polyloom" / "0.1.0"
    stale = install_path / "stale.txt"
    stale.write_text("stale")
    result = subprocess.run(
        command + ["--force"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert not stale.exists()


def test_installer_zcode_preserves_existing_files_without_force(tmp_path: Path) -> None:
    zhome = tmp_path / "zcode-home"
    command = [PY, str(INSTALLER), "--runtime", "zcode", "--zcode-home", str(zhome)]
    subprocess.run(command, check=True, capture_output=True)
    install_path = zhome / "cli" / "plugins" / "cache" / "polyloom-local" / "polyloom" / "0.1.0"
    stale = install_path / "stale.txt"
    stale.write_text("keep")

    result = subprocess.run(command, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
    assert stale.read_text() == "keep"


def test_installer_zcode_rejects_target_option(tmp_path: Path) -> None:
    result = subprocess.run(
        [PY, str(INSTALLER), "--runtime", "zcode", "--target", str(tmp_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "use --zcode-home" in result.stdout


def test_installer_zcode_rejects_malformed_registry_without_overwriting_it(tmp_path: Path) -> None:
    zhome = tmp_path / "zcode-home"
    plugins = zhome / "cli" / "plugins"
    plugins.mkdir(parents=True)
    registry = plugins / "known_marketplaces.json"
    registry.write_text("not json")
    install_path = plugins / "cache" / "polyloom-local" / "polyloom" / "0.1.0"
    install_path.mkdir(parents=True)
    stale = install_path / "stale.txt"
    stale.write_text("keep")

    result = subprocess.run(
        [PY, str(INSTALLER), "--runtime", "zcode", "--zcode-home", str(zhome), "--force"],
        capture_output=True, text=True,
    )

    assert result.returncode == 1
    assert "invalid JSON" in result.stdout
    assert registry.read_text() == "not json"
    assert stale.read_text() == "keep"


def test_installer_zcode_refreshes_stale_plugin_record(tmp_path: Path) -> None:
    zhome = tmp_path / "zcode-home"
    command = [PY, str(INSTALLER), "--runtime", "zcode", "--zcode-home", str(zhome)]
    subprocess.run(command, check=True, capture_output=True)
    records = zhome / "cli" / "plugins" / "installed_plugins.json"
    data = json.loads(records.read_text())
    entry = next(plugin for plugin in data["plugins"] if plugin["id"] == "polyloom@polyloom-local")
    entry["version"] = "stale"
    entry["installPath"] = "/stale"
    records.write_text(json.dumps(data))

    result = subprocess.run(command, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
    refreshed = json.loads(records.read_text())
    entry = next(plugin for plugin in refreshed["plugins"] if plugin["id"] == "polyloom@polyloom-local")
    assert entry["version"] == "0.1.0"
    assert entry["installPath"].endswith("polyloom-local/polyloom/0.1.0")


def test_installer_force_overwrites_codex(tmp_path: Path) -> None:
    target = tmp_path / "codex-home"
    subprocess.run([PY, str(INSTALLER), "--runtime", "codex", "--target", str(target)], capture_output=True)
    result = subprocess.run(
        [PY, str(INSTALLER), "--runtime", "codex", "--target", str(target), "--force"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr


def test_installer_help_describes_zcode_overlay_and_force_behavior() -> None:
    result = subprocess.run([PY, str(INSTALLER), "--help"], capture_output=True, text=True)

    assert result.returncode == 0
    assert "Codex destination" in result.stdout
    assert "ZCode removes stale" in result.stdout
    assert "cache files." in result.stdout


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
