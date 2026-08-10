#!/usr/bin/env python3
"""Validate Polyloom's portable role contracts and runtime adapters.

The validator intentionally uses only the Python standard library and keeps the
legacy ZCode compatibility bundle separate from the canonical project team.
"""

from __future__ import annotations

from pathlib import Path
import re

from team_topology import (
    LEGACY_ZCODE_ROLES,
    PROMPT_FIELDS,
    ROLE_BY_NAME,
    ROLE_NAMES,
    ROLE_SPECS,
    WORKER_REPORT_FIELDS,
)


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "polyloom"
SKILL_DIR = ROOT / "skills" / SKILL_NAME

# Public compatibility constants retained for callers of the pre-six-role
# ZCode validator.  They never describe project-scoped Polyloom topology.
WORKERS = (
    ("lead.toml", "lead", "medium"),
    ("builder-worker.toml", "builder", "max"),
    ("runner-worker.toml", "runner", "max"),
)
PROJECT_ROLES = ROLE_NAMES


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_polyloom() -> None:
    """Validate the core skill, contracts, and plugin metadata."""

    path = SKILL_DIR / "SKILL.md"
    require(path.exists(), "Polyloom SKILL.md is missing")
    text = path.read_text(encoding="utf-8")
    require("name: polyloom" in text, "skill name must be polyloom")
    require(
        "coordination-only" in text and "independently verifies" in text,
        "skill must describe orchestrator and QA boundaries",
    )
    lowered = re.sub(r"\s+", " ", text.lower())
    require(
        "same responsible worker" in lowered and "parent may not fix" in lowered,
        "skill must route failures back without parent implementation edits",
    )
    require(
        all(field in text.lower() for field in WORKER_REPORT_FIELDS),
        "skill must define the bounded worker report",
    )
    require(
        "do not send the full parent transcript" in lowered,
        "skill must bound prompt context",
    )
    require((ROOT / ".agents" / "orchestrator.md").exists(), "six-role contract is incomplete")
    require((ROOT / ".zcode-plugin" / "plugin.json").exists(), "ZCode plugin manifest is missing")
    validate_project_adapters()
    validate_routing_documents()


def validate_skill() -> None:
    path = SKILL_DIR / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    require(text.startswith("---\n"), "SKILL.md must start with YAML frontmatter")
    parts = text.split("---", 2)
    require(len(parts) == 3, "SKILL.md frontmatter must have a closing delimiter")
    frontmatter = parts[1]
    body = parts[2].strip()

    top_level_keys = []
    for line in frontmatter.splitlines():
        if line and not line[0].isspace():
            match = re.match(r"([a-zA-Z0-9_-]+):", line)
            if match:
                top_level_keys.append(match.group(1))
    require(set(top_level_keys) == {"name", "description"}, "frontmatter must contain only name and description")
    require(
        re.search(rf"^name:\s*{re.escape(SKILL_NAME)}\s*$", frontmatter, re.MULTILINE) is not None,
        "skill name must match its folder",
    )
    require("description: >-" in frontmatter, "description must use folded YAML")
    require(bool(body), "SKILL.md body must not be empty")
    require("terra_worker" not in text and "luna_worker" not in text, "skill must use Polyloom role names")
    require((SKILL_DIR / "agents-openai.yaml").exists(), "agents-openai.yaml is missing")
    require(all(role in text for role in ROLE_NAMES), "skill must list all six project roles")


def _parse_flat_agent(path: Path) -> dict[str, str]:
    """Read the flat fields used by this validator without a TOML dependency."""

    data: dict[str, str] = {}
    wanted = {"name", "model", "model_reasoning_effort", "sandbox_mode"}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r'([a-z_]+)\s*=\s*"([^\"]*)"', line)
        if match and match.group(1) in wanted:
            data[match.group(1)] = match.group(2)
    return data


# Keep the old public helper name for downstream legacy checks.
load_agent_toml = _parse_flat_agent


def validate_worker(filename: str, name: str, effort: str) -> None:
    """Validate a legacy user-scope compatibility adapter."""

    path = ROOT / "agents" / filename
    require(path.exists(), f"{filename}: compatibility agent manifest is missing")
    text = path.read_text(encoding="utf-8")
    data = _parse_flat_agent(path)
    require(data.get("name") == name, f"{filename}: incorrect agent name")
    require(bool(data.get("model")), f"{filename}: missing model")
    require(data.get("model_reasoning_effort") == effort, f"{filename}: reasoning effort must be {effort}")
    require('developer_instructions = """' in text, f"{filename}: missing developer instructions")
    require(all(field in text for field in WORKER_REPORT_FIELDS), f"{filename}: missing bounded evidence fields")


def validate_project_agent(role: str) -> None:
    spec = ROLE_BY_NAME[role]
    path = ROOT / ".codex" / "agents" / f"{role}.toml"
    require(path.exists(), f"missing project Codex role: {role}")
    data = _parse_flat_agent(path)
    text = path.read_text(encoding="utf-8")
    require(data.get("name") == role, f"{role}: incorrect Codex name")
    require(data.get("model") == spec["model"], f"{role}: model must be {spec['model']}")
    require(data.get("model_reasoning_effort") == spec["effort"], f"{role}: effort must be {spec['effort']}")
    if spec["sandbox"] is None:
        require("sandbox_mode" not in data, f"{role}: unexpected sandbox override")
    else:
        require(data.get("sandbox_mode") == spec["sandbox"], f"{role}: sandbox must be {spec['sandbox']}")
    require('developer_instructions = """' in text, f"{role}: missing Codex instructions")
    require(role in text, f"{role}: instructions must identify role")
    require("provider" not in text.lower(), f"{role}: provider must be runtime configured")


def validate_project_adapters() -> None:
    """Validate exact six-role project files and the model/effort matrix."""

    agents_dir = ROOT / ".agents"
    claude_dir = ROOT / ".claude" / "agents"
    codex_dir = ROOT / ".codex" / "agents"
    require(agents_dir.exists(), "project .agents directory is missing")
    require(claude_dir.exists() and codex_dir.exists(), "project runtime adapter directories are missing")

    for role in ROLE_NAMES:
        contract = agents_dir / f"{role}.md"
        claude = claude_dir / f"{role}.md"
        require(contract.exists(), f"missing project role contract: {role}")
        require(claude.exists(), f"missing Claude adapter: {role}")
        ctext = claude.read_text(encoding="utf-8")
        require(ctext.startswith("---\n") and f"name: {role}" in ctext, f"invalid Claude adapter: {role}")
        require(not re.search(r"gpt-5\.6-(?:sol|terra|luna)", ctext), f"Claude adapter pins an OpenAI model: {role}")
        validate_project_agent(role)

    config = (ROOT / ".codex" / "config.toml").read_text(encoding="utf-8")
    require("model_instructions_file = \"../.agents/AGENTS.md\"" in config, "invalid Codex project config")
    require("max_concurrent_threads_per_session = 7" in config, "Codex concurrency limit must allow seven workers")
    require(not (agents_dir / "lead.md").exists(), "legacy lead role must not be a project adapter")
    require(not (agents_dir / "builder.md").exists(), "legacy builder role must not be a project adapter")


def _require_prompt_fields(path: Path) -> None:
    text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8").lower())
    for field in PROMPT_FIELDS:
        require(field in text, f"{path}: dispatch prompt is missing {field}")


def validate_routing_documents() -> None:
    """Ensure docs and contracts encode no-delegation and bounded prompts."""

    skill = SKILL_DIR / "SKILL.md"
    command = ROOT / "commands" / "polyloom.md"
    orchestrator = ROOT / ".agents" / "orchestrator.md"
    for path in (skill, command, orchestrator):
        _require_prompt_fields(path)
    for path in (skill, command, orchestrator, ROOT / "examples" / "AGENTS.md"):
        text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8").lower())
        require("3-7" in text and "disjoint" in text, f"{path}: missing bounded dev parallelism policy")
        require("shared" in text and "sequential" in text, f"{path}: missing shared-state ordering policy")

    # Core workers are orchestrator-dispatch-only. Direct user dispatch is
    # reserved for the two lifecycle support roles.
    for role in ("dev", "runner", "qa"):
        contract = re.sub(r"\s+", " ", (ROOT / ".agents" / f"{role}.md").read_text(encoding="utf-8").lower())
        require("user directly" not in contract and "user supplies" not in contract, f"{role}: direct user dispatch is forbidden")
    routing = re.sub(r"\s+", " ", (ROOT / ".agents" / "AGENTS.md").read_text(encoding="utf-8").lower())
    require("orchestrator dispatch only" in routing, "core role dispatch must be orchestrator-only")
    require("user may dispatch" in routing and "git-manager" in routing and "plane-manager" in routing, "lifecycle direct-dispatch boundary is missing")

    implementation_contract = re.sub(r"\s+", " ", (ROOT / ".agents" / "dev.md").read_text(encoding="utf-8").lower())
    runner = re.sub(r"\s+", " ", (ROOT / ".agents" / "runner.md").read_text(encoding="utf-8").lower())
    qa = re.sub(r"\s+", " ", (ROOT / ".agents" / "qa.md").read_text(encoding="utf-8").lower())
    require("autonomous" in implementation_contract and "end to end" in implementation_contract, "implementation role must be autonomous")
    require("spawn" in implementation_contract and "not" in implementation_contract, "implementation role must prohibit spawning")
    require("delegate" in implementation_contract and "not" in implementation_contract, "implementation role must prohibit delegation")
    require("delegate" in runner and "do not design architecture" in runner, "runner boundary is incomplete")
    require("read-only" in qa and "independent" in qa, "QA must be independent and read-only")

    orchestrator_text = re.sub(r"\s+", " ", orchestrator.read_text(encoding="utf-8").lower())
    require("coordination-only" in orchestrator_text and "read-only" in orchestrator_text, "orchestrator must be read-only")
    require("do not edit source" in orchestrator_text, "orchestrator must not edit repository files")
    require("same responsible worker" in orchestrator_text, "failure routing must preserve scope owner")

    command_text = command.read_text(encoding="utf-8").lower()
    require("qa independently reviews" in command_text, "command must assign independent QA")
    require("model" in command_text and "effort" in command_text, "command must document model matrix")


def validate_examples() -> None:
    policy = (ROOT / "examples" / "AGENTS.md").read_text(encoding="utf-8").lower()
    require(f"${SKILL_NAME}" in policy, "AGENTS example must load the skill")
    require(all(role in policy for role in ROLE_NAMES), "AGENTS example must describe all project roles")
    _require_prompt_fields(ROOT / "examples" / "AGENTS.md")


def validate_legacy_bundle() -> None:
    """Validate compatibility files without treating them as project roles."""

    for worker in WORKERS:
        validate_worker(*worker)
    require(set(LEGACY_ZCODE_ROLES) == {"lead", "builder", "runner"}, "legacy role aliases changed unexpectedly")


def main() -> int:
    validate_polyloom()
    validate_skill()
    validate_legacy_bundle()
    validate_examples()
    print("Validation passed: Polyloom six-role project adapters and legacy ZCode compatibility bundle.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
