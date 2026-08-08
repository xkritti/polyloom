from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"
PY = sys.executable


def fake_zcode(tmp_path: Path) -> Path:
    """Build a fake ~/.zcode layout with a disposable plugins dir."""
    cli = tmp_path / "cli"
    plugins = cli / "plugins"
    plugins.mkdir(parents=True)
    (plugins / "installed_plugins.json").write_text(json.dumps({"version": 1, "plugins": []}))
    (plugins / "known_marketplaces.json").write_text(json.dumps({"version": 1, "marketplaces": []}))
    (cli / "config.json").write_text(json.dumps({"plugins": {"enabledPlugins": {}}}))
    return tmp_path


def test_zcode_auto_install_registers_marketplace(tmp_path: Path) -> None:
    zhome = fake_zcode(tmp_path)
    result = subprocess.run(
        [PY, str(INSTALL), "--runtime", "zcode", "--zcode-home", str(zhome)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    km = json.loads((zhome / "cli" / "plugins" / "known_marketplaces.json").read_text())
    ids = [m["id"] for m in km["marketplaces"]]
    assert "polyloom-local" in ids
    entry = next(m for m in km["marketplaces"] if m["id"] == "polyloom-local")
    assert entry["source"]["source"] == "directory"
    assert entry["pluginCount"] == 1


def test_zcode_auto_install_registers_installed_plugin(tmp_path: Path) -> None:
    zhome = fake_zcode(tmp_path)
    subprocess.run([PY, str(INSTALL), "--runtime", "zcode", "--zcode-home", str(zhome)], check=True)
    ip = json.loads((zhome / "cli" / "plugins" / "installed_plugins.json").read_text())
    ids = [p["id"] for p in ip["plugins"]]
    assert "polyloom@polyloom-local" in ids
    rec = next(p for p in ip["plugins"] if p["id"] == "polyloom@polyloom-local")
    assert rec["name"] == "polyloom"
    assert rec["marketplace"] == "polyloom-local"
    assert rec["version"] == "0.1.0"
    assert rec["installPath"].endswith("polyloom-local/polyloom/0.1.0")


def test_zcode_auto_install_copies_plugin_files(tmp_path: Path) -> None:
    zhome = fake_zcode(tmp_path)
    subprocess.run([PY, str(INSTALL), "--runtime", "zcode", "--zcode-home", str(zhome)], check=True)
    install_path = zhome / "cli" / "plugins" / "cache" / "polyloom-local" / "polyloom" / "0.1.0"
    assert (install_path / ".zcode-plugin" / "plugin.json").exists()
    assert (install_path / "skills" / "polyloom" / "SKILL.md").exists()
    assert (install_path / "commands" / "polyloom.md").exists()
    assert (install_path / "commands" / "polyloom-setup.md").exists()


def test_zcode_auto_install_enables_plugin(tmp_path: Path) -> None:
    zhome = fake_zcode(tmp_path)
    subprocess.run([PY, str(INSTALL), "--runtime", "zcode", "--zcode-home", str(zhome)], check=True)
    cfg = json.loads((zhome / "cli" / "config.json").read_text())
    assert cfg["plugins"]["enabledPlugins"].get("polyloom@polyloom-local") is True


def test_zcode_auto_install_is_idempotent(tmp_path: Path) -> None:
    zhome = fake_zcode(tmp_path)
    subprocess.run([PY, str(INSTALL), "--runtime", "zcode", "--zcode-home", str(zhome)], check=True)
    subprocess.run([PY, str(INSTALL), "--runtime", "zcode", "--zcode-home", str(zhome)], check=True)
    ip = json.loads((zhome / "cli" / "plugins" / "installed_plugins.json").read_text())
    assert sum(1 for p in ip["plugins"] if p["id"] == "polyloom@polyloom-local") == 1
    km = json.loads((zhome / "cli" / "plugins" / "known_marketplaces.json").read_text())
    assert sum(1 for m in km["marketplaces"] if m["id"] == "polyloom-local") == 1


def test_zcode_auto_install_does_not_duplicate_existing_plugin(tmp_path: Path) -> None:
    zhome = fake_zcode(tmp_path)
    # pre-register polyloom as if already installed
    ip_path = zhome / "cli" / "plugins" / "installed_plugins.json"
    ip = json.loads(ip_path.read_text())
    ip["plugins"].append({
        "id": "polyloom@polyloom-local", "name": "polyloom",
        "marketplace": "polyloom-local", "version": "0.1.0",
        "installPath": str(zhome / "cli" / "plugins" / "cache" / "polyloom-local" / "polyloom" / "0.1.0"),
        "installedAt": "2026-01-01T00:00:00.000Z", "updatedAt": "2026-01-01T00:00:00.000Z",
        "scope": "user", "source": "./",
    })
    ip_path.write_text(json.dumps(ip))
    subprocess.run([PY, str(INSTALL), "--runtime", "zcode", "--zcode-home", str(zhome)], check=True)
    ip2 = json.loads(ip_path.read_text())
    assert sum(1 for p in ip2["plugins"] if p["id"] == "polyloom@polyloom-local") == 1


def test_zcode_auto_install_preserves_existing_entries(tmp_path: Path) -> None:
    zhome = fake_zcode(tmp_path)
    ip_path = zhome / "cli" / "plugins" / "installed_plugins.json"
    ip = json.loads(ip_path.read_text())
    ip["plugins"].append({"id": "other@mp", "name": "other", "marketplace": "mp", "version": "1.0.0"})
    ip_path.write_text(json.dumps(ip))
    subprocess.run([PY, str(INSTALL), "--runtime", "zcode", "--zcode-home", str(zhome)], check=True)
    ip2 = json.loads(ip_path.read_text())
    ids = [p["id"] for p in ip2["plugins"]]
    assert "other@mp" in ids
    assert "polyloom@polyloom-local" in ids


def test_zcode_auto_install_uses_correct_marketplace_path(tmp_path: Path) -> None:
    zhome = fake_zcode(tmp_path)
    subprocess.run([PY, str(INSTALL), "--runtime", "zcode", "--zcode-home", str(zhome)], check=True)
    km = json.loads((zhome / "cli" / "plugins" / "known_marketplaces.json").read_text())
    entry = next(m for m in km["marketplaces"] if m["id"] == "polyloom-local")
    assert entry["source"]["path"] == str(ROOT)