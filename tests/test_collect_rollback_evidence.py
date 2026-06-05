"""Unit tests for scripts/collect_rollback_evidence.py."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

import collect_rollback_evidence  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=str(path),
                   check=True)
    subprocess.run(["git", "config", "user.email", "[email protected]"],
                   cwd=str(path), check=True)
    subprocess.run(["git", "config", "user.name", "tester"],
                   cwd=str(path), check=True)


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    """A repo where reverting HEAD succeeds cleanly (no conflict)."""
    repo = tmp_path
    _init_repo(repo)
    (repo / "a.txt").write_text("a\n")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "base"], cwd=str(repo),
                   check=True)
    (repo / "a.txt").write_text("a\nb\n")
    (repo / "b.txt").write_text("b\n")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "second"], cwd=str(repo),
                   check=True)
    return repo


@pytest.fixture()
def conflict_repo(tmp_path: Path) -> Path:
    """A repo where reverting HEAD~1 conflicts with HEAD."""
    repo = tmp_path
    _init_repo(repo)
    (repo / "src").mkdir()
    (repo / "src" / "plans.ts").write_text("monthly=10\n")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "base"], cwd=str(repo),
                   check=True)
    # commit A: change to monthly=10,pro=10
    (repo / "src" / "plans.ts").write_text("monthly=10,pro=10\n")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "add-Pro"], cwd=str(repo),
                   check=True)
    # commit B: a different commit changes the same line
    (repo / "src" / "plans.ts").write_text("monthly=12,pro=10\n")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "raise-monthly"],
                   cwd=str(repo), check=True)
    return repo


# ---------------------------------------------------------------------------
# run_revert_dry_run
# ---------------------------------------------------------------------------

def test_clean_repo_revert_succeeds(clean_repo: Path):
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(clean_repo),
                          text=True, capture_output=True, check=True).stdout.strip()
    result = collect_rollback_evidence.run_revert_dry_run(clean_repo, sha)
    assert result["ok"] is True
    assert result["exit_code"] == 0
    assert result["unmerged"] == []
    assert result["rej"] == []
    assert result["note"] == ""


def test_conflict_repo_revert_reports_conflict(conflict_repo: Path):
    # Revert HEAD~1 on top of HEAD — these two commits change the
    # same line so the revert will conflict.
    head = subprocess.run(["git", "rev-parse", "HEAD~1"],
                          cwd=str(conflict_repo),
                          text=True, capture_output=True, check=True).stdout.strip()
    result = collect_rollback_evidence.run_revert_dry_run(conflict_repo, head)
    assert result["ok"] is False
    assert result["exit_code"] != 0
    # The conflict should be reported either via unmerged (porcelain
    # AA/AU/UA/...) or via .rej sidecars.
    assert result["unmerged"] or result["rej"]


def test_worktree_is_always_cleaned_up(clean_repo: Path):
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(clean_repo),
                          text=True, capture_output=True, check=True).stdout.strip()
    collect_rollback_evidence.run_revert_dry_run(clean_repo, sha)
    # No leftover worktree should be listed.
    code, out, _ = collect_rollback_evidence._run(
        clean_repo, "worktree", "list", "--porcelain")
    assert code == 0
    # Only the main worktree entry is acceptable.
    main_entries = [line for line in out.splitlines()
                    if line.startswith("worktree ")]
    assert len(main_entries) == 1, (
        f"leftover worktrees: {main_entries}"
    )


def test_invalid_sha_returns_error(tmp_path: Path):
    repo = tmp_path
    _init_repo(repo)
    (repo / "a.txt").write_text("a\n")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "base"], cwd=str(repo),
                   check=True)
    result = collect_rollback_evidence.run_revert_dry_run(
        repo, "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
    assert result["ok"] is False
    # Either exit_code is non-zero or note is non-empty.
    assert result["exit_code"] != 0 or result["note"]


# ---------------------------------------------------------------------------
# render_rollback_evidence
# ---------------------------------------------------------------------------

def test_render_clean_evidence():
    result = {
        "ok": True,
        "exit_code": 0,
        "stdout": "",
        "stderr": "",
        "unmerged": [],
        "orig": [],
        "rej": [],
        "note": "",
    }
    out = collect_rollback_evidence.render_rollback_evidence("abc123", result)
    assert "Exit code" in out
    assert "| 0 |" in out
    assert "Verified" in out
    assert "0 unmerged, 0 .rej" in out


def test_render_conflict_evidence():
    result = {
        "ok": False,
        "exit_code": 1,
        "stdout": "",
        "stderr": "error: could not revert abc123\nhint: ...",
        "unmerged": ["src/plans.ts"],
        "orig": [],
        "rej": ["src/plans.ts.rej"],
        "note": "",
    }
    out = collect_rollback_evidence.render_rollback_evidence("abc123", result)
    assert "Conflict" in out
    assert "| 1 |" in out
    assert "src/plans.ts" in out
    assert "1 unmerged, 1 .rej" in out
    assert "stderr" in out


def test_render_error_evidence_with_note():
    result = {
        "ok": False,
        "exit_code": 128,
        "stdout": "",
        "stderr": "fatal: bad revision",
        "unmerged": [],
        "orig": [],
        "rej": [],
        "note": "shallow repo",
    }
    out = collect_rollback_evidence.render_rollback_evidence("abc", result)
    assert "Error" in out
    assert "shallow repo" in out


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

def test_main_clean(clean_repo: Path, capsys, monkeypatch):
    monkeypatch.chdir(clean_repo)
    rc = collect_rollback_evidence.main(
        ["--repo", str(clean_repo)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Verified" in out
    assert "Exit code" in out


def test_main_conflict(conflict_repo: Path, capsys, monkeypatch):
    monkeypatch.chdir(conflict_repo)
    head_minus_1 = subprocess.run(
        ["git", "rev-parse", "HEAD~1"], cwd=str(conflict_repo),
        text=True, capture_output=True, check=True).stdout.strip()
    rc = collect_rollback_evidence.main(
        ["--repo", str(conflict_repo), "--sha", head_minus_1])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Conflict" in out
    assert "NOT CLEAN" in out


def test_main_json_mode(clean_repo: Path, capsys, monkeypatch):
    monkeypatch.chdir(clean_repo)
    rc = collect_rollback_evidence.main(
        ["--repo", str(clean_repo), "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert "sha" in payload
    assert "ok" in payload
    assert "exit_code" in payload
    assert "unmerged" in payload
    assert payload["ok"] is True
