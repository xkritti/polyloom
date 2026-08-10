"""Canonical Polyloom role topology and runtime defaults.

This module is deliberately runtime-neutral.  The project-scoped Codex
adapter uses the model/effort/sandbox values below; Claude adapters inherit
their native runtime settings.  The legacy ZCode installer may still read a
three-role compatibility team file, but that file is not the project team
topology.
"""

from __future__ import annotations

from typing import Any


ROLE_SPECS: tuple[dict[str, Any], ...] = (
    {
        "name": "orchestrator",
        "model": "gpt-5.6-sol",
        "effort": "medium",
        "sandbox": "read-only",
        "description": "Sole coordinator, integrator, and final evidence reviewer.",
    },
    {
        "name": "dev",
        "model": "gpt-5.6-luna",
        "effort": "max",
        "sandbox": None,
        "description": "Autonomous senior implementation engineer.",
    },
    {
        "name": "runner",
        "model": "gpt-5.6-luna",
        "effort": "max",
        "sandbox": None,
        "description": "Bounded general-purpose execution worker.",
    },
    {
        "name": "qa",
        "model": "gpt-5.6-terra",
        "effort": "medium",
        "sandbox": "read-only",
        "description": "Independent read-only verifier.",
    },
    {
        "name": "git-manager",
        "model": "gpt-5.6-luna",
        "effort": "medium",
        "sandbox": None,
        "description": "On-command Git and GitHub lifecycle support.",
    },
    {
        "name": "plane-manager",
        "model": "gpt-5.6-luna",
        "effort": "medium",
        "sandbox": None,
        "description": "On-command Plane lifecycle support.",
    },
)

ROLE_NAMES = tuple(spec["name"] for spec in ROLE_SPECS)
ROLE_BY_NAME = {spec["name"]: spec for spec in ROLE_SPECS}

# These names are accepted only by the legacy ZCode user-scope compatibility
# path.  They are intentionally not project roles and must not appear in
# project adapters or routing instructions.
LEGACY_ZCODE_ROLES = ("lead", "builder", "runner")
LEGACY_ROLE_ALIASES = {"lead": "orchestrator", "builder": "dev", "runner": "runner"}

# Every dispatch prompt is required to carry these fields.  Keeping the list
# in one place lets the repository validator and tests enforce the same
# contract as the human-facing skill and command.
PROMPT_FIELDS = (
    "goal",
    "exact ownership",
    "files/modules",
    "constraints",
    "acceptance criteria",
    "validation commands",
    "expected evidence",
    "dependency/order",
)

WORKER_REPORT_FIELDS = ("changed files", "checks/results", "failures", "risks")


def canonical_specs() -> tuple[dict[str, Any], ...]:
    """Return immutable-in-practice copies for callers that may mutate data."""

    return tuple(dict(spec) for spec in ROLE_SPECS)
