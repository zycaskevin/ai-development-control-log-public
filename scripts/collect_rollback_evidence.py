#!/usr/bin/env python3
"""Collect Rollback Evidence for the AI Development Control Log v0.3.

Run ``git revert --no-commit <HEAD_SHA>`` against the working tree, capture
the exit code, conflict markers, and any auto-generated .orig / .rej
files, then emit a markdown snippet that can be pasted into the v0.3
Control Log's Section 9.5.7.

This script is read-only with respect to the user-visible branch: it
operates on a *throwaway* detached HEAD created by ``git checkout`` so the
agent's working tree is never modified.

The v0.2 9.5.7 said "revertible" without exercising the path. v0.3 makes
that claim falsifiable: if a conflict appears, the snippet records it,
and the validator can refuse to mark the log as `Verified`.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

REPO_DEFAULT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Git plumbing
# ---------------------------------------------------------------------------

def _run(repo: Path, *args: str, timeout: int = 60) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            ["git", *args],
            cwd=str(repo),
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError:
        return 127, "", f"git not found"
    except subprocess.TimeoutExpired:
        return 124, "", f"git {' '.join(args)} timeout after {timeout}s"


def get_head(repo: Path) -> str:
    code, out, err = _run(repo, "rev-parse", "HEAD")
    if code != 0:
        raise RuntimeError(f"git rev-parse HEAD failed: {err.strip()[:200]}")
    return out.strip()


def list_conflict_artifacts(repo: Path) -> dict[str, list[str]]:
    """Files that ``git status`` reports as unmerged or that have the
    well-known conflict-marker sidecar names (.orig / .rej)."""
    code, out, _ = _run(repo, "status", "--porcelain")
    artifacts: dict[str, list[str]] = {
        "unmerged": [],
        "orig": [],
        "rej": [],
    }
    for line in out.splitlines():
        if not line:
            continue
        # Unmerged entries have "UU", "AA", "DD", "AU", "UA", etc. in the
        # first two columns of the porcelain status.
        xy = line[:2]
        path = line[3:].strip().strip('"')
        if "U" in xy or xy in {"AA", "DD"}:
            artifacts["unmerged"].append(path)
    # Walk the working tree for .orig / .rej sidecars left by revert.
    for path in repo.rglob("*.orig"):
        if ".git" in path.parts:
            continue
        artifacts["orig"].append(str(path.relative_to(repo)))
    for path in repo.rglob("*.rej"):
        if ".git" in path.parts:
            continue
        artifacts["rej"].append(str(path.relative_to(repo)))
    return artifacts


def run_revert_dry_run(repo: Path, sha: str) -> dict:
    """Run ``git revert --no-commit`` on a throwaway detached HEAD and
    collect everything we need to fill 9.5.7.

    Strategy:
      1. Find the current branch tip (or fall back to HEAD).
      2. Create a throwaway worktree at that tip.
      3. ``git revert --no-commit <sha>`` inside the worktree — this
         tests the realistic question "what happens if I revert <sha>
         right now, on top of the current branch tip?"
      4. Capture exit code, stderr, conflict artifacts.
      5. Always clean up the worktree, even on failure.
    """
    worktree_dir = Path(tempfile.mkdtemp(prefix="v03-revert-"))
    try:
        # Resolve the tip to check out. Prefer the current branch's
        # tip; fall back to HEAD.
        tip = "HEAD"
        code, out, _ = _run(repo, "symbolic-ref", "--short", "HEAD")
        if code == 0 and out.strip():
            tip = out.strip()

        code_add, _, err_add = _run(
            repo, "worktree", "add", "--detach", str(worktree_dir), tip
        )
        if code_add != 0:
            return {
                "ok": False,
                "exit_code": code_add,
                "stderr": err_add.strip(),
                "stdout": "",
                "unmerged": [],
                "orig": [],
                "rej": [],
                "note": (
                    f"Could not create throwaway worktree at {tip}. "
                    "Is the repo shallow? Aborting."
                ),
            }

        rev_code, rev_out, rev_err = _run(
            worktree_dir,
            "revert", "--no-commit", "--no-edit", sha,
        )
        artifacts = list_conflict_artifacts(worktree_dir)
        return {
            "ok": rev_code == 0 and not artifacts["unmerged"]
                  and not artifacts["rej"],
            "exit_code": rev_code,
            "stdout": rev_out.strip(),
            "stderr": rev_err.strip(),
            "unmerged": artifacts["unmerged"],
            "orig": artifacts["orig"],
            "rej": artifacts["rej"],
            "note": "",
        }
    finally:
        # Always remove the throwaway worktree, even on failure.
        _run(repo, "worktree", "remove", "--force", str(worktree_dir),
             timeout=30)
        shutil.rmtree(worktree_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_rollback_evidence(sha: str, result: dict) -> str:
    """Produce a 9.5.7-ready markdown snippet.

    v0.2 9.5.7 columns: Rollback step | Command | Verified by
    v0.3 9.5.7 columns: Rollback step | Command | Exit code | Conflict
                         markers | Verified by
    """
    status = (
        "Verified" if result["ok"]
        else "Conflict" if result["unmerged"] or result["rej"]
        else "Error"
    )
    lines = [
        f"### 9.5.7 Rollback Evidence (v0.3 — actually exercised)",
        "",
        f"- **HEAD at time of evidence:** `{sha}`",
        f"- **Revert command:** `git revert --no-commit --no-edit {sha}`",
        f"- **Exit code:** `{result['exit_code']}`",
        f"- **Status:** {status}",
    ]
    if result["unmerged"]:
        lines.append(f"- **Unmerged files:** {', '.join(f'`{p}`' for p in result['unmerged'])}")
    if result["rej"]:
        lines.append(f"- **Rejected hunks (.rej):** {', '.join(f'`{p}`' for p in result['rej'])}")
    if result["orig"]:
        lines.append(f"- **Conflict sidecars (.orig):** {', '.join(f'`{p}`' for p in result['orig'])}")
    if result["stderr"]:
        # Trim to the most relevant slice (last 20 lines) to keep the
        # log readable.
        tail = "\n".join(result["stderr"].splitlines()[-20:])
        lines += ["", "**stderr (tail):**", "```text", tail, "```"]
    if result["note"]:
        lines += ["", f"**note:** {result['note']}"]

    lines += [
        "",
        "| Rollback step | Command | Exit code | Conflict markers | Verified by |",
        "|---|---|---:|---|---|",
        f"| Revert commit | `git revert --no-commit --no-edit {sha}` | "
        f"{result['exit_code']} | "
        f"{len(result['unmerged'])} unmerged, {len(result['rej'])} .rej | "
        f"{'throwaway worktree at current tip, then reverted' if result['ok'] else 'NOT CLEAN — see above'} |",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO_DEFAULT)
    parser.add_argument("--sha", default=None,
                        help="Commit to revert (default: HEAD).")
    parser.add_argument("--json", action="store_true",
                        help="Emit machine-readable JSON instead of markdown.")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    if not (repo / ".git").exists():
        print(f"error: {repo} is not a git repo", file=sys.stderr)
        return 1

    try:
        sha = args.sha or get_head(repo)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    result = run_revert_dry_run(repo, sha)
    if args.json:
        payload = {"sha": sha, **result}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if result["ok"] else 0  # never fail: capture, don't crash

    print(render_rollback_evidence(sha, result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
