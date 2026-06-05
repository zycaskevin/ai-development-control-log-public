#!/usr/bin/env python3
"""Collect objective evidence for the AI Development Control Log v0.2.

Outputs two markdown snippets that an agent (or human) can paste into
Section 9.5.1 (Changed Files) and Section 9.5.3 (Test Result) of a v0.2 log.

This script is intentionally read-only. It does not modify the repo.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Sequence

REPO_DEFAULT = Path(__file__).resolve().parents[1]
DEFAULT_TEST_CMDS: list[list[str]] = [
    ["pytest", "-q", "--maxfail=1"],
    ["npm", "test", "--silent"],
    ["vitest", "run", "--reporter=basic"],
    ["go", "test", "./..."],
]


def run(cmd: Sequence[str], cwd: Path, timeout: int = 60) -> tuple[int, str, str]:
    try:
        p = subprocess.run(list(cmd), cwd=str(cwd), text=True,
                           capture_output=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError:
        return 127, "", f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s: {' '.join(cmd)}"


def collect_changed_files(repo: Path, base: str) -> tuple[list[dict], str]:
    # Use two-dot diff: "what HEAD has that base does not".
    # Three-dot (base...HEAD) is the merge-base diff, which is empty when
    # the current branch IS base, which is the most common case for an
    # agent finishing a feature branch.
    code, name_status, err1 = run(
        ["git", "diff", "--name-status", f"{base}..HEAD"], cwd=repo)
    code2, numstat, err2 = run(
        ["git", "diff", "--numstat", f"{base}..HEAD"], cwd=repo)
    if code != 0 or code2 != 0:
        return [], f"git diff failed: {(err1 or err2)[:200]}"

    numstat_map: dict[str, tuple[int, int]] = {}
    for line in numstat.splitlines():
        m = re.match(r"^(\d+|-)\s+(\d+|-)\s+(.+)$", line)
        if m:
            add = -1 if m.group(1) == "-" else int(m.group(1))
            dele = -1 if m.group(2) == "-" else int(m.group(2))
            numstat_map[m.group(3)] = (add, dele)

    files: list[dict] = []
    for line in name_status.splitlines():
        parts = line.split("\t", 2)
        if len(parts) < 2:
            continue
        status, path = parts[0], parts[1]
        add, dele = numstat_map.get(path, (0, 0))
        files.append({"status": status, "path": path,
                     "added": add, "deleted": dele})
    return files, ""


def render_changed_files(files: list[dict]) -> str:
    if not files:
        return "（無變更，或 base ref 與 HEAD 相同）"
    lines = [
        "| Path | Status | Lines +/- |",
        "|---|---|---:|",
    ]
    for f in files:
        lines.append(f"| `{f['path']}` | {f['status']} | +{f['added']} / -{f['deleted']} |")
    return "\n".join(lines)


def run_test_command(repo: Path, cmd: list[str], timeout: int) -> dict:
    code, out, err = run(cmd, cwd=repo, timeout=timeout)
    # 0   → tool ran, exited cleanly     → Pass
    # >0  → tool ran, exited with error  → Fail
    # 127 → tool not installed           → Skip
    # 124 → timeout                      → Skip
    if code == 0:
        result = "Pass"
    elif code in (127, 124):
        result = "Skip"
    elif code is not None and code > 0:
        result = "Fail"
    else:
        result = "Skip"
    return {
        "cmd": " ".join(cmd),
        "code": code,
        "stdout": (out or "").strip(),
        "stderr": (err or "").strip(),
        "result": result,
    }


def detect_test_command(repo: Path) -> list[str] | None:
    for path, cmd in [
        ("pytest.ini", DEFAULT_TEST_CMDS[0]),
        ("pyproject.toml", DEFAULT_TEST_CMDS[0]),
        ("package.json", DEFAULT_TEST_CMDS[1]),
        ("go.mod", DEFAULT_TEST_CMDS[3]),
    ]:
        if (repo / path).exists():
            return list(cmd)
    return None


def render_test_result(result: dict) -> str:
    head = (
        f"| {result['cmd']} | see below | "
        f"{result['result']} |\n\n"
        f"```text\n$ {result['cmd']}\n\n"
    )
    body = ""
    if result["stdout"]:
        body += result["stdout"][-2000:] + "\n"
    if result["stderr"]:
        body += "\n[stderr]\n" + result["stderr"][-1000:] + "\n"
    head += body + "```"
    return head


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO_DEFAULT)
    parser.add_argument("--base", default="main",
                        help="Base ref to diff against (default: main)")
    parser.add_argument("--test-cmd", action="append", default=None,
                        help="Test command to run (repeatable). "
                             "Accepts a shell-style string which will be "
                             "split with shlex (e.g. "
                             "'pytest -v tests/test_sample.py'). "
                             "Auto-detected if omitted.")
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--json", action="store_true",
                        help="Emit machine-readable JSON instead of markdown")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    if not (repo / ".git").exists():
        print(f"error: {repo} is not a git repo", file=sys.stderr)
        return 1

    files, err = collect_changed_files(repo, args.base)
    if err:
        print(f"error: {err}", file=sys.stderr)
        return 2

    test_cmd = args.test_cmd or ([detect_test_command(repo)] if detect_test_command(repo) else [])
    # Each --test-cmd is a shell-style string. Split with shlex so that
    # `--test-cmd "pytest -v tests/x.py"` becomes ["pytest", "-v", "tests/x.py"].
    resolved_test_cmds: list[list[str]] = []
    for raw in test_cmd:
        if raw is None:
            continue
        if isinstance(raw, str):
            resolved_test_cmds.append(shlex.split(raw))
        else:
            resolved_test_cmds.append(list(raw))
    test_results = [run_test_command(repo, c, args.timeout) for c in resolved_test_cmds] if resolved_test_cmds else []

    if args.json:
        print(json.dumps({"changed_files": files, "test_results": test_results},
                         ensure_ascii=False, indent=2))
        return 0

    print("## 9.5.1 Changed Files (objective)\n")
    print("How this was filled:")
    print("```bash")
    print(f"git diff --name-status {args.base}..HEAD")
    print(f"git diff --numstat {args.base}..HEAD")
    print("```\n")
    print(render_changed_files(files))
    print()
    if test_results:
        print("## 9.5.3 Test Result (raw output)\n")
        for r in test_results:
            print(render_test_result(r))
            print()
    else:
        print("## 9.5.3 Test Result")
        print("\nNo test command detected and none passed via --test-cmd. "
              "Fill this section manually with raw output.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
