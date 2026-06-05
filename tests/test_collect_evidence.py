"""Unit tests for scripts/collect_evidence.py."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import collect_evidence  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    """Create a real git repo on a feature branch with three commits.

    Mirrors a realistic agent workflow: a `main` branch with a base commit,
    and a `feat/test` branch with two follow-up commits. The diff is
    meaningful only because HEAD and main are on different refs.
    """
    repo = tmp_path
    run = subprocess.run

    def git(*args, check=True):
        r = run(["git", *args], cwd=str(repo), text=True,
                capture_output=True, check=check)
        return r.stdout.strip()

    git("init", "-q", "-b", "main")
    git("config", "user.email", "[email protected]")
    git("config", "user.name", "tester")
    # base commit on main
    (repo / "a.txt").write_text("hello\n", encoding="utf-8")
    (repo / "keep.txt").write_text("untouched\n", encoding="utf-8")
    git("add", "a.txt", "keep.txt")
    git("commit", "-q", "-m", "base")
    # feature branch
    git("checkout", "-q", "-b", "feat/test")
    # second commit on feat: modify a.txt, add b.txt
    (repo / "a.txt").write_text("hello world\n", encoding="utf-8")
    (repo / "b.txt").write_text("new file\n", encoding="utf-8")
    (repo / "c.txt").write_text("to be deleted\n", encoding="utf-8")
    git("add", "a.txt", "b.txt", "c.txt")
    git("commit", "-q", "-m", "second")
    # third commit: delete c.txt
    (repo / "c.txt").unlink()
    git("add", "-A")
    git("commit", "-q", "-m", "remove c")
    return repo


def _make_pytest_repo(repo: Path) -> None:
    """Make the fixture repo look like a Python project with one passing test."""
    (repo / "pytest.ini").write_text("[pytest]\naddopts = -q\n", encoding="utf-8")
    (repo / "tests").mkdir(exist_ok=True)
    (repo / "tests" / "test_sample.py").write_text(
        "def test_ok():\n    assert 1 + 1 == 2\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True,
                   text=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "add pytest"], cwd=str(repo),
                   check=True, text=True, capture_output=True)


# ---------------------------------------------------------------------------
# collect_changed_files
# ---------------------------------------------------------------------------

def test_collect_changed_files_lists_real_diff(git_repo: Path):
    files, err = collect_evidence.collect_changed_files(git_repo, "main")
    assert err == "", err
    paths = {f["path"] for f in files}
    # a.txt was modified, b.txt added. c.txt was added then deleted in
    # the same feature branch, so it is a net-zero change and won't
    # appear in `git diff main..HEAD`. This is correct git behavior,
    # not a bug.
    assert paths == {"a.txt", "b.txt"}, paths

    by_path = {f["path"]: f for f in files}
    assert by_path["a.txt"]["status"].startswith("M")
    assert by_path["a.txt"]["added"] == 1
    assert by_path["a.txt"]["deleted"] == 1
    assert by_path["b.txt"]["status"].startswith("A")
    assert by_path["b.txt"]["added"] == 1


def test_collect_changed_files_empty_when_no_diff(git_repo: Path):
    # Diff against HEAD..HEAD should be empty.
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(git_repo),
                          text=True, capture_output=True, check=True).stdout.strip()
    files, err = collect_evidence.collect_changed_files(git_repo, head)
    assert err == ""
    assert files == []


def test_collect_changed_files_invalid_base(git_repo: Path):
    files, err = collect_evidence.collect_changed_files(git_repo, "no-such-ref")
    assert files == []
    assert err  # an error message is present


# ---------------------------------------------------------------------------
# render_changed_files
# ---------------------------------------------------------------------------

def test_render_changed_files_with_data():
    files = [
        {"path": "a.txt", "status": "M", "added": 1, "deleted": 1},
        {"path": "b.txt", "status": "A", "added": 3, "deleted": 0},
    ]
    out = collect_evidence.render_changed_files(files)
    assert "| Path | Status | Lines +/- |" in out
    assert "| `a.txt` | M | +1 / -1 |" in out
    assert "| `b.txt` | A | +3 / -0 |" in out


def test_render_changed_files_empty():
    out = collect_evidence.render_changed_files([])
    assert "（無變更" in out


# ---------------------------------------------------------------------------
# detect_test_command
# ---------------------------------------------------------------------------

def test_detect_test_command_pytest_ini(git_repo: Path):
    (git_repo / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    cmd = collect_evidence.detect_test_command(git_repo)
    assert cmd is not None
    assert cmd[0] == "pytest"


def test_detect_test_command_pyproject_toml(git_repo: Path):
    (git_repo / "pyproject.toml").write_text("[project]\nname='x'\n",
                                             encoding="utf-8")
    cmd = collect_evidence.detect_test_command(git_repo)
    assert cmd is not None
    assert cmd[0] == "pytest"


def test_detect_test_command_package_json(git_repo: Path):
    (git_repo / "package.json").write_text("{}", encoding="utf-8")
    cmd = collect_evidence.detect_test_command(git_repo)
    assert cmd is not None
    assert cmd[0] == "npm"


def test_detect_test_command_go_mod(git_repo: Path):
    (git_repo / "go.mod").write_text("module x\n\ngo 1.22\n", encoding="utf-8")
    cmd = collect_evidence.detect_test_command(git_repo)
    assert cmd is not None
    assert cmd[0] == "go"


def test_detect_test_command_none(git_repo: Path):
    cmd = collect_evidence.detect_test_command(git_repo)
    assert cmd is None


# ---------------------------------------------------------------------------
# run_test_command
# ---------------------------------------------------------------------------

def test_run_test_command_passing(git_repo: Path, tmp_path: Path):
    _make_pytest_repo(git_repo)
    if shutil.which("pytest") is None:
        pytest.skip("pytest not installed on this machine")
    # Use a clean working dir inside the repo so pytest discovers the file.
    result = collect_evidence.run_test_command(
        git_repo, ["pytest", "-v", "tests/test_sample.py"], timeout=60)
    assert result["code"] == 0, result["stderr"]
    assert result["result"] == "Pass"
    assert "1 passed" in result["stdout"]


def test_run_test_command_failing(git_repo: Path):
    (git_repo / "tests").mkdir(exist_ok=True)
    (git_repo / "tests" / "test_bad.py").write_text(
        "def test_bad():\n    assert False\n", encoding="utf-8")
    if shutil.which("pytest") is None:
        pytest.skip("pytest not installed on this machine")
    result = collect_evidence.run_test_command(
        git_repo, ["pytest", "-v", "tests/test_bad.py"], timeout=60)
    assert result["code"] != 0
    assert result["result"] == "Fail"


def test_run_test_command_missing_tool(tmp_path: Path):
    result = collect_evidence.run_test_command(
        tmp_path, ["definitely-not-a-real-tool-xyz"], timeout=10)
    assert result["code"] == 127
    assert result["result"] == "Skip"
    assert "command not found" in result["stderr"]


def test_run_test_command_timeout(tmp_path: Path):
    # `sleep 99` is universally available on Linux. If we hit 1s timeout,
    # we expect code 124 and result "Skip".
    result = collect_evidence.run_test_command(
        tmp_path, ["sleep", "99"], timeout=1)
    assert result["code"] == 124
    assert result["result"] == "Skip"


# ---------------------------------------------------------------------------
# render_test_result
# ---------------------------------------------------------------------------

def test_render_test_result_passing():
    r = {
        "cmd": "pytest -q",
        "code": 0,
        "stdout": "1 passed in 0.01s\n",
        "stderr": "",
        "result": "Pass",
    }
    out = collect_evidence.render_test_result(r)
    assert "| pytest -q | see below | Pass |" in out
    assert "1 passed in 0.01s" in out
    assert "```text" in out


def test_render_test_result_includes_stderr():
    r = {
        "cmd": "pytest -q",
        "code": 1,
        "stdout": "1 failed\n",
        "stderr": "FAILED tests/x.py::test_y\n",
        "result": "Fail",
    }
    out = collect_evidence.render_test_result(r)
    assert "[stderr]" in out
    assert "FAILED tests/x.py::test_y" in out


# ---------------------------------------------------------------------------
# main() — end-to-end against the real fixture
# ---------------------------------------------------------------------------

def test_main_json_mode(git_repo: Path, capsys, monkeypatch):
    monkeypatch.chdir(git_repo)
    rc = collect_evidence.main(["--repo", str(git_repo), "--base", "main",
                                "--json"])
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert "changed_files" in payload
    assert "test_results" in payload
    paths = {f["path"] for f in payload["changed_files"]}
    # See test_collect_changed_files_lists_real_diff for why c.txt is absent.
    assert paths == {"a.txt", "b.txt"}


def test_main_markdown_mode(git_repo: Path, capsys, monkeypatch):
    monkeypatch.chdir(git_repo)
    rc = collect_evidence.main(["--repo", str(git_repo), "--base", "main"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "## 9.5.1 Changed Files (objective)" in out
    assert "git diff --name-status main..HEAD" in out
    assert "| `a.txt` | M | +1 / -1 |" in out


def test_main_with_explicit_test_cmd(git_repo: Path, capsys, monkeypatch):
    _make_pytest_repo(git_repo)
    monkeypatch.chdir(git_repo)
    if shutil.which("pytest") is None:
        pytest.skip("pytest not installed on this machine")
    rc = collect_evidence.main([
        "--repo", str(git_repo), "--base", "main",
        "--test-cmd", "pytest -v tests/test_sample.py",
    ])
    assert rc == 0
    out = capsys.readouterr().out
    assert "## 9.5.3 Test Result (raw output)" in out
    assert "1 passed" in out


def test_main_no_test_command_hint(git_repo: Path, capsys, monkeypatch):
    monkeypatch.chdir(git_repo)
    rc = collect_evidence.main(["--repo", str(git_repo), "--base", "main"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "No test command detected" in out
