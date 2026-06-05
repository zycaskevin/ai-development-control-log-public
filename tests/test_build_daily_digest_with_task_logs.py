"""Tests for v0.5 daily digest integration with task-level control logs."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

import build_daily_digest  # noqa: E402
import collect_task_logs  # noqa: E402
import validate_daily_digest  # noqa: E402


TASK_LOG = """# Task Control Log — v0.5 task logs

## Metadata

- Date: 2026-06-05
- Actor: Example Agent
- Repo: ai-development-control-log

## User explicitly asked

- 使用者說「繼續」，接續 v0.5。
- 使用者要 daily digest 看得出哪些是使用者要求、哪些是 AI 自決。

## AI self-decided

- Decision: 先做 task-level control log，不先加 LLM 美化。
  Rationale: 沒有可靠資料來源時，LLM 只會把 git 猜測寫得更漂亮。
  Should have asked user first: no

## Spec deviations

- Deviation: v0.4 roadmap 原本寫 v0.5 是 multi-agent digest。
  Original spec: v0.5 multi-agent digests.
  Actual implementation: v0.5 task-level control log.
  Reason: 先解決 user asked / AI self-decided 資料來源。
  Needs user confirmation: no

## High-risk touchpoints

- Path / operation: scripts/build_daily_digest.py
  Risk type: daily report source-of-truth logic
  User confirmed: yes
  Rollback path: revert v0.5 commit and keep v0.4.1

## Verification evidence

- Claim: parser extracts task-log evidence.
  Verification type: unit
  Raw evidence: python -m pytest tests/test_collect_task_logs.py -q

## Rollback evidence

- Failure scenario: v0.5 digest confuses the user.
  Rollback command / toggle / procedure: use v0.4.1 release tag.
  Verified rollback: partial
"""


def _activity():
    return build_daily_digest.DailyActivity(
        commits=[
            build_daily_digest.CommitInfo(
                sha='abc1234',
                author='Example Agent',
                date='2026-06-05T08:00:00Z',
                subject='feat: add task-level control logs',
            )
        ],
        touched_paths=['scripts/build_daily_digest.py'],
        since='24 hours ago',
        until='now',
    )


def _validate(tmp_path: Path, text: str):
    path = tmp_path / 'digest.md'
    path.write_text(text, encoding='utf-8')
    return validate_daily_digest.validate_digest(path)


def test_digest_uses_task_logs_for_user_requested_section(tmp_path):
    task_logs = [collect_task_logs.parse_task_log_text(TASK_LOG, source='task.md')]

    text = build_daily_digest.render_digest(
        date='2026-06-05',
        activity=_activity(),
        timezone='Asia/Taipei',
        task_logs=task_logs,
    )

    assert '使用者說「繼續」，接續 v0.5。' in text
    assert '使用者要 daily digest 看得出哪些是使用者要求' in text
    assert '自動模式只能看到 git 證據' not in text
    assert _validate(tmp_path, text) == []


def test_digest_uses_task_logs_for_ai_self_decision_section(tmp_path):
    task_logs = [collect_task_logs.parse_task_log_text(TASK_LOG, source='task.md')]

    text = build_daily_digest.render_digest(
        date='2026-06-05',
        activity=_activity(),
        timezone='Asia/Taipei',
        task_logs=task_logs,
    )

    assert '先做 task-level control log，不先加 LLM 美化。' in text
    assert '沒有可靠資料來源時' in text
    assert '沒有從 commit 本身可靠讀到' not in text
    assert '。。' not in text
    assert _validate(tmp_path, text) == []


def test_digest_uses_task_logs_for_deviation_verification_and_rollback(tmp_path):
    task_logs = [collect_task_logs.parse_task_log_text(TASK_LOG, source='task.md')]

    text = build_daily_digest.render_digest(
        date='2026-06-05',
        activity=_activity(),
        timezone='Asia/Taipei',
        task_logs=task_logs,
    )

    assert 'v0.4 roadmap 原本寫 v0.5 是 multi-agent digest。' in text
    assert 'parser extracts task-log evidence.' in text
    assert 'python -m pytest tests/test_collect_task_logs.py -q' in text
    assert 'use v0.4.1 release tag.' in text
    assert _validate(tmp_path, text) == []


def test_digest_without_task_logs_keeps_v04_fallback_language(tmp_path):
    text = build_daily_digest.render_digest(
        date='2026-06-05',
        activity=_activity(),
        timezone='Asia/Taipei',
        task_logs=[],
    )

    assert '自動模式只能看到 git 證據' in text
    assert 'logs/tasks/YYYY-MM-DD-<slug>.md' in text
    assert 'templates/task-control-log' in text
    assert '沒有從 commit 本身可靠讀到' in text
    assert _validate(tmp_path, text) == []


def test_digest_does_not_render_secret_values_from_task_logs(tmp_path):
    secret = 'https://' + 'hooks.slack.com' + '/services/T000/B000/FAKE_SECRET_SHOULD_NOT_APPEAR'
    task_log_text = TASK_LOG.replace(
        'python -m pytest tests/test_collect_task_logs.py -q',
        f'env SLACK_WEBHOOK_URL={secret} python scripts/send_daily_digest.py digest.md --provider slack',
    )
    task_logs = [collect_task_logs.parse_task_log_text(task_log_text, source='task.md')]

    text = build_daily_digest.render_digest(
        date='2026-06-05',
        activity=_activity(),
        timezone='Asia/Taipei',
        task_logs=task_logs,
    )

    assert secret not in text
    assert '[REDACTED]' in text
    assert _validate(tmp_path, text) == []
