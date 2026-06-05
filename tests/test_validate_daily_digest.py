"""Tests for scripts/validate_daily_digest.py.

These tests pin down the contract the validator promises to the digest
author: a real digest answers all 7 questions, has a 1-minute summary
near the top, and has a feedback section.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_daily_digest as vdd  # noqa: E402


# A complete, valid zh-TW digest body that should pass.
VALID_ZH_TW_BODY = """# Control Log｜2026-06-05｜Example Agent

## 📋 0. 1 分鐘版（給老闆看）

| 欄位 | 值 |
|---|---|
| 昨天 AI 做了幾件事 | 7 |
| 待你決定幾件 | 2 |
| 這份你看得懂嗎？ | ✅ / ⚠️ / ❌（見 §8） |

## 0. 語言與讀者設定

| 欄位 | 值 |
|---|---|
| 輸出語言 | zh-TW |

## 1. AI 做了什麼？

| 動作 | 是使用者叫的？ | 是 AI 自決的？ | 證據 |
|---|---|---|---|
| 修 v0.2.1 | ✅ | ❌ | PR #15 |

## 2. 哪些是你明確要求的？

- 修 v0.2.1 預設不要自動寄

## 3. 哪些是 AI 自己決定的？

| AI 自決的決定 | 為什麼這樣做 | 替代方案 | 該不該先問使用者？ |
|---|---|---|---|
| 改 7 區段標題 | v0.4 規格 | 保持 5 區段 | ✅ 是 |

## 4. 偏離原本規格了嗎？

| 偏離 | 原本規格 | 實際做法 | 原因 | 是否需要使用者確認？ |
|---|---|---|---|---|
| 無 | 7 區段 | 7 區段 | 無 | ✅ |

## 5. 有沒有碰到高風險操作？

| 風險項 | 是否觸發 | 處理方式 | 是否已取得使用者確認？ |
|---|---|---|---|
| 對外發布 / 客戶訊息 | ❌ |  |  |

## 6. 驗證了什麼？沒驗證什麼？

| 結論 | 可信度 | 證據（真實輸出，不是「應該過了」） |
|---|---|---|
| 7 區段都有 | ✅ 已真實驗證 | pytest 49 passed |

## 7. 出事怎麼退？

| 失敗情境 | 退路 | 已驗證可退？ |
|---|---|---|
| 區段缺漏 | validator 會 fail | ✅ |

## 8. 這份 digest 你看得懂嗎？

請回覆 ✅ / ⚠️ / ❌ 其中一個。
"""


def _write(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


def test_valid_zh_tw_digest_passes(tmp_path: Path):
    p = _write(tmp_path, "valid.md", VALID_ZH_TW_BODY)
    errors = vdd.validate_digest(p)
    assert errors == [], f"expected no errors, got: {errors}"


def test_missing_1_minute_block_fails(tmp_path: Path):
    body = VALID_ZH_TW_BODY.replace("## 📋 0. 1 分鐘版（給老闆看）\n", "")
    p = _write(tmp_path, "no1min.md", body)
    errors = vdd.validate_digest(p)
    assert any("1-minute summary" in e for e in errors), errors


def test_missing_q1_fails(tmp_path: Path):
    body = VALID_ZH_TW_BODY.replace("## 1. AI 做了什麼？\n", "")
    p = _write(tmp_path, "noq1.md", body)
    errors = vdd.validate_digest(p)
    assert any("q1_what_ai_did" in e for e in errors), errors


def test_missing_q2_fails(tmp_path: Path):
    body = VALID_ZH_TW_BODY.replace("## 2. 哪些是你明確要求的？\n", "")
    p = _write(tmp_path, "noq2.md", body)
    errors = vdd.validate_digest(p)
    assert any("q2_user_required" in e for e in errors), errors


def test_missing_q3_fails(tmp_path: Path):
    body = VALID_ZH_TW_BODY.replace("## 3. 哪些是 AI 自己決定的？\n", "")
    p = _write(tmp_path, "noq3.md", body)
    errors = vdd.validate_digest(p)
    assert any("q3_ai_decisions" in e for e in errors), errors


def test_missing_q4_fails(tmp_path: Path):
    body = VALID_ZH_TW_BODY.replace("## 4. 偏離原本規格了嗎？\n", "")
    p = _write(tmp_path, "noq4.md", body)
    errors = vdd.validate_digest(p)
    assert any("q4_deviations" in e for e in errors), errors


def test_missing_q5_fails(tmp_path: Path):
    body = VALID_ZH_TW_BODY.replace("## 5. 有沒有碰到高風險操作？\n", "")
    p = _write(tmp_path, "noq5.md", body)
    errors = vdd.validate_digest(p)
    assert any("q5_high_risk" in e for e in errors), errors


def test_missing_q6_fails(tmp_path: Path):
    body = VALID_ZH_TW_BODY.replace("## 6. 驗證了什麼？沒驗證什麼？\n", "")
    p = _write(tmp_path, "noq6.md", body)
    errors = vdd.validate_digest(p)
    assert any("q6_verification" in e for e in errors), errors


def test_missing_q7_fails(tmp_path: Path):
    body = VALID_ZH_TW_BODY.replace("## 7. 出事怎麼退？\n", "")
    p = _write(tmp_path, "noq7.md", body)
    errors = vdd.validate_digest(p)
    assert any("q7_rollback" in e for e in errors), errors


def test_missing_q8_feedback_fails(tmp_path: Path):
    body = VALID_ZH_TW_BODY.replace("## 8. 這份 digest 你看得懂嗎？\n", "")
    p = _write(tmp_path, "noq8.md", body)
    errors = vdd.validate_digest(p)
    assert any("q8_feedback" in e for e in errors), errors


def test_empty_section_body_fails(tmp_path: Path):
    # Wipe Q1's body entirely (no table, no rows) so the section has
    # no real content after the heading.
    body = VALID_ZH_TW_BODY
    # Find the Q1 block including its table and replace it with just
    # the heading followed by an empty line and a blank quote.
    body = re.sub(
        r"(## 1\. AI 做了什麼？\n\n)\|.*?\n\|[-:|\s]+\n(?:\|.*?\n)*",
        r"\1\n",
        body,
        count=1,
        flags=re.DOTALL,
    )
    p = _write(tmp_path, "emptybody.md", body)
    errors = vdd.validate_digest(p)
    assert any("q1_what_ai_did" in e and "empty" in e for e in errors), errors


def test_q8_feedback_section_does_not_require_content(tmp_path: Path):
    # §8 is the reader's reply; author may leave it blank.
    body = VALID_ZH_TW_BODY.replace(
        "請回覆 ✅ / ⚠️ / ❌ 其中一個。", ""
    )
    p = _write(tmp_path, "blankq8.md", body)
    errors = vdd.validate_digest(p)
    # The empty §8 should NOT be flagged as "is empty" because we don't
    # require content for feedback section.
    assert not any("q8_feedback" in e and "empty" in e for e in errors), errors


def test_en_aliases_accepted(tmp_path: Path):
    body = """# Daily AI Decision Digest

## 📋 Section 0. 1-Minute Version (for the boss)

| Field | Value |
|---|---|
| x | 1 |

## 0. Language and Audience

| Field | Value |
|---|---|
| Output language | en |

## 1. What did AI do?

| Action | User-requested? | AI-self-decided? | Evidence |
|---|---|---|---|
| did thing | ✅ | ❌ | link |

## 2. What did the user explicitly require?

- the user wanted this

## 3. What did AI decide on its own?

| AI-made decision | Why | Alternatives | Ask first? |
|---|---|---|---|
| chose | because | else | ✅ |

## 4. Did it deviate from the spec?

| Deviation | Original | Actual | Reason | Confirm? |
|---|---|---|---|---|
| none | spec | match | none | ✅ |

## 5. Did it touch any high-risk operation?

| Risk | Triggered | How | Confirmed? |
|---|---|---|---|
| External publish | ❌ |  |  |

## 6. What was verified? What was not?

| Conclusion | Credibility | Evidence |
|---|---|---|
| ok | ✅ | raw output |

## 7. If it breaks, how do you roll back?

| Failure | Rollback | Verified? |
|---|---|---|
| fail | git revert | ✅ |

## 8. Can you read this digest?

Please reply ✅ / ⚠️ / ❌.
"""
    p = _write(tmp_path, "en.md", body)
    errors = vdd.validate_digest(p)
    assert errors == [], f"EN aliases should work, got: {errors}"


def test_en_section_prefix_content_is_not_misread_as_empty(tmp_path: Path):
    body = """# Daily AI Decision Digest

## 📋 Section 0. 1-Minute Version (for the boss)

- readable summary

## Section 0. Language and Audience

- Output language: en

## Section 1. What did AI do?

- implemented the daily digest workflow

## Section 2. What did the user explicitly require?

- make it readable

## Section 3. What did AI decide on its own?

- kept delivery opt-in

## Section 4. Did it deviate from the spec?

- no deviation found

## Section 5. Did it touch any high-risk operation?

- no production data touched

## Section 6. What was verified? What was not?

- tests passed; external delivery not enabled

## Section 7. If it breaks, how do you roll back?

- set DELIVERY_PROVIDER to none

## Section 8. Can you read this digest?

- please reply
"""
    p = _write(tmp_path, "en-section-prefix.md", body)
    errors = vdd.validate_digest(p)
    assert errors == [], f"Section-prefixed headings should not be treated as empty: {errors}"


def test_main_with_dir_scans_all_md(tmp_path: Path):
    (tmp_path / "a.md").write_text(VALID_ZH_TW_BODY, encoding="utf-8")
    (tmp_path / "b.md").write_text("garbage", encoding="utf-8")
    rc = vdd.main.__wrapped__([str(tmp_path)]) if hasattr(vdd.main, "__wrapped__") else None
    # Direct call to main with sys.argv patching
    import subprocess
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "validate_daily_digest.py"), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0, "garbage file should fail validation"
    assert "FAIL" in result.stdout


def test_empty_file_fails(tmp_path: Path):
    p = _write(tmp_path, "empty.md", "")
    errors = vdd.validate_digest(p)
    assert any("empty file" in e for e in errors), errors


def test_nonexistent_file_fails(tmp_path: Path):
    p = tmp_path / "does-not-exist.md"
    errors = vdd.validate_digest(p)
    assert any("not found" in e for e in errors), errors


def test_real_template_passes(tmp_path: Path):
    """The actual template file should pass validation (it is a valid
    starting point with all sections and 1-minute block in place)."""
    template = REPO_ROOT / "templates" / "daily-decision-digest.zh-TW.md"
    if not template.exists():
        pytest.skip("template not found")
    errors = vdd.validate_digest(template)
    assert errors == [], f"template should be valid, got: {errors}"


def test_real_en_template_passes(tmp_path: Path):
    template = REPO_ROOT / "templates" / "daily-decision-digest.en.md"
    if not template.exists():
        pytest.skip("en template not found")
    errors = vdd.validate_digest(template)
    assert errors == [], f"en template should be valid, got: {errors}"


def test_section_content_after_heading_handles_missing():
    assert vdd.section_content_after_heading("no heading here", "missing") == ""


def test_has_any_heading_basic():
    text = "## 1. AI 做了什麼？\n"
    assert vdd.has_any_heading(text, "AI 做了什麼？")


def test_is_template_placeholder():
    assert vdd._is_template_placeholder("")
    assert vdd._is_template_placeholder("\n\n   \n")
    assert vdd._is_template_placeholder("(direct quote or message reference)")
    assert vdd._is_template_placeholder("(auto-counted from §1)")
    assert not vdd._is_template_placeholder("actual content here")
    assert not vdd._is_template_placeholder("| a | b | c |")
