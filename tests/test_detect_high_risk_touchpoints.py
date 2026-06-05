"""Unit tests for scripts/detect_high_risk_touchpoints.py."""
import subprocess
import sys
from pathlib import Path

import pytest

import detect_high_risk_touchpoints as dht  # noqa: E402


@pytest.fixture()
def sample_config(tmp_path: Path) -> Path:
    p = tmp_path / "patterns.yml"
    p.write_text(
        "version: 1\n"
        "categories:\n"
        "  - id: payment\n"
        "    reason: 'payment touchpoint'\n"
        "    patterns:\n"
        "      - '**/billing*/**'\n"
        "      - '**/payment*/**'\n"
        "  - id: db-schema\n"
        "    reason: 'db touchpoint'\n"
        "    patterns:\n"
        "      - '**/migrations/**'\n"
        "exempt_paths:\n"
        "  - '**/tests/**'\n"
        "  - '**/*.test.*'\n"
    )
    return p


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=str(path),
                   check=True)
    subprocess.run(["git", "config", "user.email", "[email protected]"],
                   cwd=str(path), check=True)
    subprocess.run(["git", "config", "user.name", "tester"],
                   cwd=str(path), check=True)


# ---------------------------------------------------------------------------
# Pattern matching helpers
# ---------------------------------------------------------------------------

def test_is_exempt():
    assert dht.is_exempt("tests/test_x.py", ["**/tests/**"])
    assert dht.is_exempt("src/x.test.ts", ["**/*.test.*"])
    assert not dht.is_exempt("src/x.ts", ["**/tests/**", "**/*.test.*"])


def test_match_category():
    assert dht.match_category(
        "src/billing/invoice.ts", ["**/billing*/**"])
    assert not dht.match_category(
        "src/config/plans.ts", ["**/billing*/**"])


# ---------------------------------------------------------------------------
# classify()
# ---------------------------------------------------------------------------

def test_classify_matches_payment():
    cfg = {
        "categories": [
            {"id": "payment", "reason": "money",
             "patterns": ["**/billing*/**"]},
        ],
        "exempt_paths": ["**/tests/**"],
    }
    out = dht.classify(["src/billing/invoice.ts",
                        "src/config/plans.ts"], cfg)
    assert "payment" in out
    assert out["payment"][0]["path"] == "src/billing/invoice.ts"
    assert "config" not in out


def test_classify_excludes_tests():
    cfg = {
        "categories": [
            {"id": "payment", "reason": "money",
             "patterns": ["**/billing*/**"]},
        ],
        "exempt_paths": ["**/tests/**"],
    }
    out = dht.classify(["tests/billing/test_invoice.py",
                        "src/billing/invoice.ts"], cfg)
    # Tests are exempt.
    assert out == {"payment": [{"path": "src/billing/invoice.ts",
                                 "reason": "money"}]}


def test_classify_file_in_multiple_categories():
    cfg = {
        "categories": [
            {"id": "payment", "reason": "money",
             "patterns": ["**/billing*/**"]},
            {"id": "db-schema", "reason": "schema",
             "patterns": ["**/billing*/**"]},
        ],
        "exempt_paths": [],
    }
    out = dht.classify(["src/billing/invoice.ts"], cfg)
    assert "payment" in out
    assert "db-schema" in out


def test_classify_empty():
    out = dht.classify([], {
        "categories": [{"id": "x", "reason": "x", "patterns": ["**/x/**"]}],
        "exempt_paths": [],
    })
    assert out == {}


# ---------------------------------------------------------------------------
# list_changed_files
# ---------------------------------------------------------------------------

def test_list_changed_files_on_branch(tmp_path: Path):
    """When base is reachable from HEAD, the two-dot diff returns
    the actual change set."""
    repo = tmp_path
    _init_repo(repo)
    (repo / "a.txt").write_text("a\n")
    (repo / "b.txt").write_text("b\n")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "base"], cwd=str(repo),
                   check=True)
    subprocess.run(["git", "checkout", "-q", "-b", "feat"], cwd=str(repo),
                   check=True)
    (repo / "a.txt").write_text("a2\n")
    (repo / "c.txt").write_text("c\n")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "second"], cwd=str(repo),
                   check=True)
    files = dht.list_changed_files(repo, "main")
    assert "a.txt" in files
    assert "c.txt" in files


def test_list_changed_files_fallback_to_head_diff(tmp_path: Path):
    """When the user commits directly on main (so main and HEAD point
    to the same commit), the two-dot diff is empty. The detector
    should fall back to HEAD~1..HEAD so the user still gets useful
    output."""
    repo = tmp_path
    _init_repo(repo)
    (repo / "a.txt").write_text("a\n")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "base"], cwd=str(repo),
                   check=True)
    (repo / "a.txt").write_text("a2\n")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "on-main"], cwd=str(repo),
                   check=True)
    files = dht.list_changed_files(repo, "main")
    assert "a.txt" in files


# ---------------------------------------------------------------------------
# render_touchpoints
# ---------------------------------------------------------------------------

def test_render_empty():
    out = dht.render_touchpoints({})
    assert "No high-risk touchpoints detected" in out


def test_render_with_data():
    out = dht.render_touchpoints({
        "payment": [{"path": "src/billing/invoice.ts",
                     "reason": "money"}],
    })
    assert "Touchpoint type" in out
    assert "src/billing/invoice.ts" in out
    assert "payment" in out
    assert "MUST NOT be deleted" in out


# ---------------------------------------------------------------------------
# main() — five real-world shapes from the spec
# ---------------------------------------------------------------------------

def _make_repo_with_files(tmp_path: Path, files: dict[str, str]) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    for rel, content in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "base"], cwd=str(repo),
                   check=True)
    # Now create a feature commit on top.
    subprocess.run(["git", "checkout", "-q", "-b", "feat"], cwd=str(repo),
                   check=True)
    # The "files" argument also serves as the diff for the feature
    # commit (re-write the same files with new content).
    for rel, content in files.items():
        (repo / rel).write_text(content + "\n")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "feat"], cwd=str(repo),
                   check=True)
    return repo


def test_main_node_billing(tmp_path: Path, sample_config: Path):
    """Node-style billing change: src/billing/invoice.ts."""
    repo = _make_repo_with_files(
        tmp_path, {"src/billing/invoice.ts": "module.exports = {}"})
    rc = dht.main(["--repo", str(repo), "--config", str(sample_config),
                  "--base", "main"])
    assert rc == 0
    out, _ = _capture_main(dht, ["--repo", str(repo),
                                  "--config", str(sample_config),
                                  "--base", "main"])
    assert "payment" in out
    assert "src/billing/invoice.ts" in out


def test_main_prisma_migration(tmp_path: Path, sample_config: Path):
    repo = _make_repo_with_files(
        tmp_path, {"prisma/schema.prisma": "model User {}"})
    out, _ = _capture_main(dht, ["--repo", str(repo),
                                  "--config", str(sample_config),
                                  "--base", "main"])
    # No categories match schema.prisma; expect empty.
    assert "No high-risk touchpoints detected" in out


def test_main_auth0_update(tmp_path: Path, sample_config: Path):
    repo = _make_repo_with_files(
        tmp_path, {"src/auth/handlers.ts": "export const auth = 1"})
    out, _ = _capture_main(dht, ["--repo", str(repo),
                                  "--config", str(sample_config),
                                  "--base", "main"])
    # No auth/permission category in sample_config; expect empty.
    assert "No high-risk touchpoints detected" in out


def test_main_env_change(tmp_path: Path, sample_config: Path):
    repo = _make_repo_with_files(
        tmp_path, {".env.production": "FOO=bar"})
    out, _ = _capture_main(dht, ["--repo", str(repo),
                                  "--config", str(sample_config),
                                  "--base", "main"])
    assert "No high-risk touchpoints detected" in out


def test_main_webhook_change(tmp_path: Path, sample_config: Path):
    repo = _make_repo_with_files(
        tmp_path, {"src/webhooks/stripe.ts": "export const x = 1"})
    out, _ = _capture_main(dht, ["--repo", str(repo),
                                  "--config", str(sample_config),
                                  "--base", "main"])
    assert "No high-risk touchpoints detected" in out


def test_main_json_mode(tmp_path: Path, sample_config: Path, capsys):
    repo = _make_repo_with_files(
        tmp_path, {"src/billing/invoice.ts": "x"})
    rc = dht.main(["--repo", str(repo), "--config", str(sample_config),
                  "--base", "main", "--json"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "changed_files" in out
    assert "classified" in out
    assert "payment" in out  # JSON output includes the category


def _capture_main(module, argv: list[str]) -> tuple[str, int]:
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = module.main(argv)
    return buf.getvalue(), rc
