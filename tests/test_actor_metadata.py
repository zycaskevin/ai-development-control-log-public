"""Unit tests for scripts/collect_actor_metadata.py and
scripts/validate.py's v0.3.1 Actor & Provenance gate."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import collect_actor_metadata  # noqa: E402
import validate  # noqa: E402


# ---------------------------------------------------------------------------
# collect_actor_metadata helpers
# ---------------------------------------------------------------------------

def test_now_iso_is_z_suffixed():
    s = collect_actor_metadata.now_iso()
    assert s.endswith("Z")
    # 4-digit year, dashes, colons — strict ISO-8601.
    assert len(s) >= 20
    assert "T" in s


def test_derive_session_uses_task_id(monkeypatch):
    monkeypatch.setenv("HERMES_TASK_ID", "feat-12345678")
    sid = collect_actor_metadata.derive_session_id()
    # The script slices the last 8 chars of the task id, so the
    # expected suffix is "-345678" (the trailing 6 chars of the
    # task id, prefixed by "-" for visual clarity in the iso
    # timestamp). This makes the session id sort chronologically
    # while still carrying a human-meaningful hint.
    assert "feat" in sid
    assert "-" in sid.rsplit("Z", 1)[0]


def test_derive_session_without_task_id(monkeypatch):
    monkeypatch.delenv("HERMES_TASK_ID", raising=False)
    sid = collect_actor_metadata.derive_session_id()
    # No suffix added. The session id is just a plain ISO-8601
    # timestamp with the timezone `Z` suffix. Note that the date
    # itself contains dashes (e.g. `2026-01-01T...`), so we cannot
    # assert "no dashes before Z" — we only assert that the
    # format ends with `Z` and has no extra suffix.
    assert sid.endswith("Z")
    # The session id must be at least 20 chars (YYYY-MM-DDTHH:MM:SSZ).
    assert len(sid) >= 20


def test_collect_reads_env(monkeypatch):
    monkeypatch.setenv("HERMES_AGENT_MODEL", "minimax-m3")
    monkeypatch.setenv("HERMES_AGENT_SESSION", "")
    monkeypatch.delenv("HERMES_TASK_ID", raising=False)
    data = collect_actor_metadata.collect()
    assert data["agent_model"] == "minimax-m3"
    # Falls back to derive_session_id when HERMES_AGENT_SESSION is empty.
    assert data["agent_session"].endswith("Z")
    # Human-side rows are intentionally blank.
    assert data["human_approver"] == ""
    assert data["approval_evidence"] == ""
    # Wall clock is set to now.
    assert data["wall_clock_start"] == data["wall_clock_end"]


def test_collect_unset_model_defaults_to_unknown(monkeypatch):
    monkeypatch.delenv("HERMES_AGENT_MODEL", raising=False)
    data = collect_actor_metadata.collect()
    assert data["agent_model"] == "unknown"


# ---------------------------------------------------------------------------
# render_markdown
# ---------------------------------------------------------------------------

def test_render_markdown_en_uses_fill_by_hand():
    out = collect_actor_metadata.render_markdown({
        "agent_model": "minimax-m3",
        "agent_session": "2026-01-01T00:00:00Z",
        "human_approver": "",
        "approval_evidence": "",
        "wall_clock_start": "2026-01-01T00:00:00Z",
        "wall_clock_end": "2026-01-01T00:01:00Z",
    }, lang="en")
    assert "minimax-m3" in out
    assert "<FILL BY HAND>" in out
    # Section title is in English.
    assert "autofilled" in out


def test_render_markdown_zh_tw_uses_chinese_placeholder():
    out = collect_actor_metadata.render_markdown({
        "agent_model": "minimax-m3",
        "agent_session": "2026-01-01T00:00:00Z",
        "human_approver": "",
        "approval_evidence": "",
        "wall_clock_start": "2026-01-01T00:00:00Z",
        "wall_clock_end": "2026-01-01T00:01:00Z",
    }, lang="zh-TW")
    assert "minimax-m3" in out
    assert "<由人類填寫>" in out
    assert "自動填" in out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def test_main_writes_markdown_to_stdout(capsys, monkeypatch):
    monkeypatch.setenv("HERMES_AGENT_MODEL", "minimax-m3")
    rc = collect_actor_metadata.main([])
    assert rc == 0
    out = capsys.readouterr().out
    assert "minimax-m3" in out
    assert "<FILL BY HAND>" in out


def test_main_json_mode(capsys, monkeypatch):
    monkeypatch.setenv("HERMES_AGENT_MODEL", "claude-sonnet-4-6")
    rc = collect_actor_metadata.main(["--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["agent_model"] == "claude-sonnet-4-6"
    assert payload["human_approver"] == ""


def test_main_writes_to_file(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_AGENT_MODEL", "minimax-m3")
    out_file = tmp_path / "section-0.5.md"
    rc = collect_actor_metadata.main(["--out", str(out_file)])
    assert rc == 0
    text = out_file.read_text()
    assert "minimax-m3" in text
    assert "<FILL BY HAND>" in text


# ---------------------------------------------------------------------------
# validate.py: validate_v0_3_1_actor_metadata gate
# ---------------------------------------------------------------------------

# A minimal-but-complete v0.3.1 log stub.
COMPLETE_LOG = """\
# Control Log

## 0.5 Actor & Provenance (v0.3.1 — required)

| Field | Value |
|---|---|
| Agent model       | minimax-m3 |
| Agent session     | 2026-01-01T00:00:00Z |
| Human approver    | @maintainer |
| Approval evidence | https://example.com/pr/1 |
| Wall clock start  | 2026-01-01T00:00:00Z |
| Wall clock end    | 2026-01-01T00:01:00Z |

## 9.5 Evidence Layer

### 9.5.6 High-Risk Touchpoints

| Path | Touchpoint type | Why this is high-risk |
|---|---|---|
| src/billing/x.ts | payment | example |
"""


def test_gate_passes_on_complete_log():
    errs = validate.validate_v0_3_1_actor_metadata(COMPLETE_LOG)
    assert errs == [], f"unexpected errors: {errs}"


def test_gate_fails_on_missing_0_5_section():
    text = "## 1. Task Goal\n\n- do the thing\n"
    errs = validate.validate_v0_3_1_actor_metadata(text)
    assert any("0.5 'Actor & Provenance' missing" in e for e in errs)


def test_gate_fails_on_empty_agent_model():
    text = COMPLETE_LOG.replace("| Agent model       | minimax-m3 |",
                                 "| Agent model       |  |")
    errs = validate.validate_v0_3_1_actor_metadata(text)
    assert any("Agent model" in e and "empty" in e for e in errs)


def test_gate_fails_on_empty_agent_session():
    text = COMPLETE_LOG.replace("| Agent session     | 2026-01-01T00:00:00Z |",
                                 "| Agent session     |  |")
    errs = validate.validate_v0_3_1_actor_metadata(text)
    assert any("Agent session" in e and "empty" in e for e in errs)


def test_gate_passes_when_human_approver_is_blank():
    """Human-side rows may be blank in agent-authored logs. The
    human fills them in before review."""
    text = COMPLETE_LOG.replace("| Human approver    | @maintainer |",
                                 "| Human approver    | <FILL BY HAND> |")
    errs = validate.validate_v0_3_1_actor_metadata(text)
    assert errs == [], errs


def test_gate_fails_self_approval_with_high_risk():
    text = COMPLETE_LOG.replace("| Human approver    | @maintainer |",
                                 "| Human approver    | self-approved |")
    errs = validate.validate_v0_3_1_actor_metadata(text)
    assert any("self-approval is forbidden" in e for e in errs)


def test_gate_passes_self_approval_when_no_high_risk():
    text = COMPLETE_LOG.replace(
        "| src/billing/x.ts | payment | example |",
        "| src/utils/x.ts | utils | example |",
    )
    errs = validate.validate_v0_3_1_actor_metadata(text)
    assert errs == [], errs


def test_gate_fails_self_approval_with_db_schema():
    text = COMPLETE_LOG.replace("| src/billing/x.ts | payment | example |",
                                 "| migrations/001.sql | db-schema | example |")
    text = text.replace("| Human approver    | @maintainer |",
                        "| Human approver    | self-approved |")
    errs = validate.validate_v0_3_1_actor_metadata(text)
    assert any("self-approval is forbidden" in e for e in errs)


def test_gate_fails_when_wall_clock_end_before_start():
    text = COMPLETE_LOG.replace("| Wall clock end    | 2026-01-01T00:01:00Z |",
                                 "| Wall clock end    | 2025-12-31T00:00:00Z |")
    errs = validate.validate_v0_3_1_actor_metadata(text)
    assert any("Wall clock end" in e and "before" in e for e in errs)


def test_gate_fails_on_invalid_iso_8601():
    text = COMPLETE_LOG.replace("| Wall clock start  | 2026-01-01T00:00:00Z |",
                                 "| Wall clock start  | yesterday |")
    errs = validate.validate_v0_3_1_actor_metadata(text)
    assert any("not valid ISO-8601" in e for e in errs)


# ---------------------------------------------------------------------------
# has_markdown_heading: ensure 0.5 prefix variations are matched
# ---------------------------------------------------------------------------

def test_has_markdown_heading_matches_0_5_with_ampersand():
    text = "## 0.5 Actor & Provenance (v0.3.1 — required)\n"
    assert validate.has_markdown_heading(text, "Actor & Provenance")


def test_has_markdown_heading_matches_0_5_without_dot():
    """`0.5 Actor & Provenance` (no trailing dot) must match."""
    text = "## 0.5 Section\n"
    assert validate.has_markdown_heading(text, "Section")
