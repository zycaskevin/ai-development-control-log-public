#!/usr/bin/env python3
"""Auto-detect high-risk touchpoints for the AI Development Control Log v0.3.

Scan a git repo's working-tree + staged changes against
``config/high_risk_patterns.yml`` and produce a markdown snippet that
the agent can paste into the v0.3 Control Log's Section 9.5.6.

Key idea: 9.5.6 must NOT be self-reported by the agent. The patterns
come from the working tree (a path the agent can change) and the config
(a path the agent should not be allowed to edit silently).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import yaml  # If PyYAML is missing the import here will fail loudly
            # at module load. CLI runs surface a friendlier message
            # via the check in main().

REPO_DEFAULT = Path(__file__).resolve().parents[1]
CONFIG_DEFAULT = REPO_DEFAULT / "config" / "high_risk_patterns.yml"


# ---------------------------------------------------------------------------
# Git + config loading
# ---------------------------------------------------------------------------

def _run(repo: Path, *args: str) -> tuple[int, str, str]:
    try:
        p = subprocess.run(["git", *args], cwd=str(repo), text=True,
                           capture_output=True, check=False)
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError:
        return 127, "", "git not found"


def list_changed_files(repo: Path, base: str) -> list[str]:
    """Return paths that differ between <base>..HEAD, plus uncommitted
    untracked + modified files. We use the same two-dot diff as
    collect_evidence.py.

    Edge case: when the user commits directly on `main` (so HEAD and
    `main` point to the same commit), `main..HEAD` is empty. In that
    case fall back to the last commit's parents — the changes from
    HEAD~1 to HEAD — which is what the user almost certainly means.
    """
    paths: set[str] = set()
    code, out, _ = _run(repo, "diff", "--name-only", f"{base}..HEAD")
    if code == 0 and out.strip():
        paths.update(line.strip() for line in out.splitlines() if line.strip())
    else:
        # Fall back to the most recent commit's diff.
        code, out, _ = _run(repo, "diff", "--name-only", "HEAD~1..HEAD")
        if code == 0:
            paths.update(line.strip() for line in out.splitlines() if line.strip())
    # Plus uncommitted working-tree changes.
    code, out, _ = _run(repo, "status", "--porcelain")
    if code == 0:
        for line in out.splitlines():
            if len(line) < 4:
                continue
            path = line[3:].strip().strip('"')
            # Skip renames where the path is "old -> new".
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            paths.add(path)
    return sorted(paths)


def load_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Pattern matching
# ---------------------------------------------------------------------------

def _glob_to_regex(pat: str) -> str:
    """Convert a gitignore-style glob to a regex.

    - `**` matches zero or more path segments (including `/`)
    - `*` matches zero or more characters within a single segment
      (no `/`)
    """
    import re
    out = []
    i = 0
    while i < len(pat):
        c = pat[i]
        if c == "*":
            if i + 1 < len(pat) and pat[i + 1] == "*":
                out.append(".*")
                i += 2
                # consume following slash so '**/' matches zero or
                # more path segments, not just any prefix
                if i < len(pat) and pat[i] == "/":
                    i += 1
                    out.append("(.*/)?")
                else:
                    out.append(".*")
            else:
                out.append("[^/]*")
                i += 1
        else:
            out.append(re.escape(c))
            i += 1
    return "^" + "".join(out) + "$"


def is_exempt(path: str, exempt: list[str]) -> bool:
    import re
    for pat in exempt:
        if re.match(_glob_to_regex(pat), path):
            return True
    return False


def match_category(path: str, patterns: list[str]) -> bool:
    import re
    for pat in patterns:
        if re.match(_glob_to_regex(pat), path):
            return True
    return False


def classify(changed: Iterable[str], config: dict) -> dict[str, list[dict]]:
    """Return {category_id: [{path, reason}, ...]} for each file that
    matches a category, excluding exempt paths."""
    out: dict[str, list[dict]] = {}
    exempt = config.get("exempt_paths", [])
    for cat in config.get("categories", []):
        cid = cat["id"]
        reason = cat.get("reason", "")
        patterns = cat.get("patterns", [])
        for path in changed:
            if is_exempt(path, exempt):
                continue
            if match_category(path, patterns):
                out.setdefault(cid, []).append({"path": path, "reason": reason})
    return out


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_touchpoints(classified: dict[str, list[dict]]) -> str:
    """Produce a 9.5.6-ready markdown snippet.

    v0.2 9.5.6: agent hand-wrote the table.
    v0.3 9.5.6: this table is auto-generated from the working tree.
    The agent MAY add explanatory notes but MUST NOT delete detected
    rows. Validation refuses to pass a v0.3 log where a flagged path
    is missing from the table.
    """
    if not classified:
        return (
            "### 9.5.6 High-Risk Touchpoints (v0.3 — auto-detected)\n\n"
            "No high-risk touchpoints detected. Working tree diff matched "
            "none of the patterns in `config/high_risk_patterns.yml`.\n"
        )
    lines = [
        "### 9.5.6 High-Risk Touchpoints (v0.3 — auto-detected)",
        "",
        "Generated by `scripts/detect_high_risk_touchpoints.py` from "
        "the working tree + staged changes. Rows MUST NOT be deleted; "
        "agents may only add notes per row.",
        "",
        "| Path | Touchpoint type | Why this is high-risk |",
        "|---|---|---|",
    ]
    for cid, items in classified.items():
        for item in items:
            lines.append(
                f"| `{item['path']}` | {cid} | {item['reason']} |"
            )
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO_DEFAULT)
    parser.add_argument("--base", default="main",
                        help="Base ref to diff against (default: main)")
    parser.add_argument("--config", type=Path, default=CONFIG_DEFAULT)
    parser.add_argument("--json", action="store_true",
                        help="Emit machine-readable JSON instead of markdown.")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    if not (repo / ".git").exists():
        print(f"error: {repo} is not a git repo", file=sys.stderr)
        return 1
    if not args.config.exists():
        print(f"error: config not found: {args.config}", file=sys.stderr)
        return 1

    try:
        config = load_config(args.config)
    except ImportError:
        # Defensive: if for any reason yaml is missing at runtime
        # (e.g. user uninstalled it after a previous run), surface
        # a friendly message rather than crashing with a stack trace.
        print("error: PyYAML is required. Install with `pip install pyyaml`.",
              file=sys.stderr)
        return 2
    changed = list_changed_files(repo, args.base)
    classified = classify(changed, config)

    if args.json:
        print(json.dumps({"changed_files": changed,
                          "classified": classified},
                         ensure_ascii=False, indent=2))
        return 0
    print(render_touchpoints(classified))
    return 0


if __name__ == "__main__":
    sys.exit(main())
