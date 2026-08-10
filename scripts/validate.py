#!/usr/bin/env python3
"""Validate the public skill package using only the Python standard library."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "polyloom"
SKILL_DIR = ROOT / "skills" / SKILL_NAME
WORKERS = (
    ("lead.toml", "lead", "medium"),
    ("builder-worker.toml", "builder", "high"),
    ("runner-worker.toml", "runner", "low"),
)
PROJECT_ROLES = ("orchestrator", "dev", "runner", "qa", "git-manager", "plane-manager")


def validate_polyloom() -> None:
    path = SKILL_DIR / "SKILL.md"
    require(path.exists(), "Polyloom SKILL.md is missing")
    text = path.read_text(encoding="utf-8")
    require("name: polyloom" in text, "skill name must be polyloom")
    require((ROOT / ".agents" / "orchestrator.md").exists(), "six-role contract is incomplete")
    require("Never modify source files directly" in text or "Do not mutate source files" in text or "coordination-only" in text, "orchestrator must be coordination-only")
    require("Delegate every repository mutation" in text or "delegate" in text.lower(), "orchestrator must delegate mutations")
    manifest = ROOT / ".zcode-plugin" / "plugin.json"
    require(manifest.exists(), "ZCode plugin manifest is missing")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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

    require(
        set(top_level_keys) == {"name", "description"},
        "frontmatter must contain only name and description",
    )
    require(
        re.search(rf"^name:\s*{re.escape(SKILL_NAME)}\s*$", frontmatter, re.MULTILINE)
        is not None,
        "skill name must match its folder",
    )
    require("description: >-" in frontmatter, "description must use folded YAML")
    require(bool(body), "SKILL.md body must not be empty")
    require("terra_worker" not in text and "luna_worker" not in text, "skill must use Polyloom role names")
    require((SKILL_DIR / "agents-openai.yaml").exists(), "agents-openai.yaml is missing")


def load_agent_toml(path: Path) -> dict[str, str]:
    """Read the flat agent settings needed by this validator on Python 3.9+."""
    data: dict[str, str] = {}
    wanted = {"name", "model", "model_reasoning_effort"}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r'([a-z_]+)\s*=\s*"([^\"]*)"', line)
        if match and match.group(1) in wanted:
            data[match.group(1)] = match.group(2)
    return data


def validate_worker(filename: str, name: str, effort: str) -> None:
    path = ROOT / "agents" / filename
    require(path.exists(), f"{filename}: agent manifest is missing")
    text = path.read_text(encoding="utf-8")
    data = load_agent_toml(path)

    require(data.get("name") == name, f"{filename}: incorrect agent name")
    require(bool(data.get("model")), f"{filename}: missing model")
    require(
        data.get("model_reasoning_effort") == effort,
        f"{filename}: reasoning effort must be {effort}",
    )
    require(
        'developer_instructions = """' in text,
        f"{filename}: missing developer instructions",
    )


def validate_examples() -> None:
    policy = (ROOT / "examples" / "AGENTS.md").read_text(encoding="utf-8")
    require(f"${SKILL_NAME}" in policy, "AGENTS example must load the skill")
    require("dev" in policy and "runner" in policy and "qa" in policy, "AGENTS example must describe project roles")


def validate_project_adapters() -> None:
    for role in PROJECT_ROLES:
        path = ROOT / ".agents" / f"{role}.md"
        require(path.exists(), f"missing project role: {role}")
        claude = ROOT / ".claude" / "agents" / f"{role}.md"
        codex = ROOT / ".codex" / "agents" / f"{role}.toml"
        require(claude.exists() and codex.exists(), f"missing runtime adapter: {role}")
        ctext = claude.read_text(encoding="utf-8")
        ttext = codex.read_text(encoding="utf-8")
        require(ctext.startswith("---\n") and "name:" in ctext, f"invalid Claude adapter: {role}")
        require('name = "' + role + '"' in ttext, f"invalid Codex agent name: {role}")
        require('developer_instructions = """' in ttext, f"missing Codex instructions: {role}")
        require('model = "gpt-5.6-luna"' in ttext, f"Codex role must use Luna: {role}")
        require('model_reasoning_effort = "max"' in ttext, f"Codex role must use max effort: {role}")
        require(not re.search(r"(?im)^provider\s*[=:]", ctext + "\n" + ttext), f"pinned provider: {role}")
    config = (ROOT / ".codex" / "config.toml").read_text(encoding="utf-8")
    require("model_instructions_file = \"../.agents/AGENTS.md\"" in config, "invalid Codex project config")
    require("max_concurrent_threads_per_session = 6" in config, "Codex concurrency limit is missing")


def main() -> int:
    validate_polyloom()
    validate_skill()
    for worker in WORKERS:
        validate_worker(*worker)
    validate_examples()
    validate_project_adapters()
    print("Validation passed: Polyloom project adapters and legacy ZCode bundle.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
