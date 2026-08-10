"""Regression tests for the canonical Polyloom six-role topology."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from team_topology import PROMPT_FIELDS, ROLE_SPECS, ROLE_NAMES  # noqa: E402
import validate  # noqa: E402


def fields(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r'([a-z_]+)\s*=\s*"([^\"]*)"', line)
        if match:
            values[match.group(1)] = match.group(2)
    return values


def test_project_topology_is_exactly_six_roles() -> None:
    assert ROLE_NAMES == (
        "orchestrator",
        "dev",
        "runner",
        "qa",
        "git-manager",
        "plane-manager",
    )
    assert tuple(spec["name"] for spec in ROLE_SPECS) == ROLE_NAMES


def test_codex_model_effort_and_sandbox_matrix() -> None:
    expected = {
        "orchestrator": ("gpt-5.6-sol", "medium", "read-only"),
        "dev": ("gpt-5.6-luna", "max", None),
        "runner": ("gpt-5.6-luna", "max", None),
        "qa": ("gpt-5.6-terra", "medium", "read-only"),
        "git-manager": ("gpt-5.6-luna", "medium", None),
        "plane-manager": ("gpt-5.6-luna", "medium", None),
    }
    for role, (model, effort, sandbox) in expected.items():
        data = fields(ROOT / ".codex" / "agents" / f"{role}.toml")
        assert (data["model"], data["model_reasoning_effort"], data.get("sandbox_mode")) == (model, effort, sandbox)


def test_dispatch_payload_contract_is_documented() -> None:
    for path in (ROOT / ".agents/orchestrator.md", ROOT / "commands/polyloom.md", ROOT / "skills/polyloom/SKILL.md"):
        text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8").lower())
        assert all(field in text for field in PROMPT_FIELDS)


def test_orchestrator_dev_parallelism_is_bounded() -> None:
    docs = [ROOT / ".agents/orchestrator.md", ROOT / "skills/polyloom/SKILL.md", ROOT / "commands/polyloom.md"]
    for path in docs:
        text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8").lower())
        assert "3-7" in text
        assert "disjoint" in text
        assert "shared" in text and "sequential" in text
    config = (ROOT / ".codex/config.toml").read_text(encoding="utf-8")
    assert "max_concurrent_threads_per_session = 7" in config


def test_no_non_orchestrator_delegation_contract() -> None:
    for role in ("dev", "runner", "qa", "git-manager", "plane-manager"):
        text = (ROOT / ".agents" / f"{role}.md").read_text(encoding="utf-8").lower()
        assert "delegate" in text
        assert "spawn" in text or role in ("git-manager", "plane-manager")
    dev = (ROOT / ".agents/dev.md").read_text(encoding="utf-8").lower()
    assert "autonomous" in dev and "end to end" in dev
    assert "do not delegate" in dev


def test_core_roles_are_orchestrator_dispatch_only() -> None:
    for role in ("dev", "runner", "qa"):
        text = (ROOT / ".agents" / f"{role}.md").read_text(encoding="utf-8").lower()
        assert "user directly" not in text
        assert "user supplies" not in text
    policy = (ROOT / ".agents/AGENTS.md").read_text(encoding="utf-8").lower()
    assert "orchestrator dispatch only" in policy
    assert "user may dispatch" in policy


def test_repository_validator_enforces_topology() -> None:
    validate.validate_polyloom()
