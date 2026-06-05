"""Tests for v0.5 task-level control log parsing."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

import collect_task_logs  # noqa: E402


ZH_TASK_LOG = """# Task Control Log — v0.5 task logs

## Metadata

- Date: 2026-06-05
- Actor: Example Agent
- Repo: ai-development-control-log
- Branch: feat/v0.5-task-control-log
- Commit / PR: pending

## User explicitly asked

- 使用者說「繼續」，接續 v0.5。
- 使用者要 daily digest 看得出哪些是使用者要求、哪些是 AI 自決。

## AI self-decided

- Decision: 先做 task-level control log，不先加 LLM 美化。
  Rationale: 沒有可靠資料來源時，LLM 只會把 git 猜測寫得更漂亮。
  Should have asked user first: no
- Decision: 保留 v0.4 git fallback。
  Rationale: 沒有 task logs 的 fork 不能被 v0.5 破壞。
  Should have asked user first: no

## Spec deviations

- Deviation: v0.4 roadmap 原本寫 v0.5 是 multi-agent digest。
  Original spec: v0.5 multi-agent digests.
  Actual implementation: v0.5 task-level control log.
  Reason: 使用者的產品問題先需要分辨 user asked / AI self-decided。
  Needs user confirmation: no

## High-risk touchpoints

- Path / operation: scripts/build_daily_digest.py
  Risk type: daily report source-of-truth logic
  User confirmed: yes
  Rollback path: revert v0.5 commit and keep v0.4.1

## Verification evidence

- Claim: parser extracts user requests and AI decisions.
  Verification type: unit
  Raw evidence: python -m pytest tests/test_collect_task_logs.py -q
- Claim: GitHub workflow still produces artifact.
  Verification type: not verified
  Raw evidence: pending after merge

## Rollback evidence

- Failure scenario: v0.5 digest confuses the user.
  Rollback command / toggle / procedure: use v0.4.1 release tag or remove --task-log-dir.
  Verified rollback: partial

## Human-readable final summary

- v0.5 adds task-level evidence so the daily digest stops guessing from git only.
"""


PLACEHOLDER_TASK_LOG = """# Task Control Log — placeholder

## User explicitly asked

- ...
- （填寫使用者明確要求）

## AI self-decided

- Decision:
  Rationale:
  Should have asked user first:

## Spec deviations

- 無

## High-risk touchpoints

- none

## Verification evidence

- Claim:
  Verification type:
  Raw evidence:

## Rollback evidence

- Failure scenario:
  Rollback command / toggle / procedure:
  Verified rollback:
"""


def test_extracts_user_explicit_requirements_from_zh_tw_log():
    result = collect_task_logs.parse_task_log_text(ZH_TASK_LOG, source='fixture.md')

    assert result.source == 'fixture.md'
    assert result.user_requests == [
        '使用者說「繼續」，接續 v0.5。',
        '使用者要 daily digest 看得出哪些是使用者要求、哪些是 AI 自決。',
    ]
    assert result.warnings == []


def test_extracts_ai_self_decisions_with_rationale():
    result = collect_task_logs.parse_task_log_text(ZH_TASK_LOG)

    assert len(result.ai_decisions) == 2
    first = result.ai_decisions[0]
    assert first.decision == '先做 task-level control log，不先加 LLM 美化。'
    assert '可靠資料來源' in first.rationale
    assert first.should_have_asked_user_first == 'no'


def test_extracts_spec_deviations():
    result = collect_task_logs.parse_task_log_text(ZH_TASK_LOG)

    assert len(result.spec_deviations) == 1
    deviation = result.spec_deviations[0]
    assert deviation.deviation == 'v0.4 roadmap 原本寫 v0.5 是 multi-agent digest。'
    assert deviation.original_spec == 'v0.5 multi-agent digests.'
    assert deviation.actual_implementation == 'v0.5 task-level control log.'
    assert deviation.needs_user_confirmation == 'no'


def test_extracts_high_risk_touchpoints():
    result = collect_task_logs.parse_task_log_text(ZH_TASK_LOG)

    assert len(result.high_risk_touchpoints) == 1
    touchpoint = result.high_risk_touchpoints[0]
    assert touchpoint.path_or_operation == 'scripts/build_daily_digest.py'
    assert touchpoint.risk_type == 'daily report source-of-truth logic'
    assert touchpoint.user_confirmed == 'yes'
    assert touchpoint.rollback_path == 'revert v0.5 commit and keep v0.4.1'


def test_extracts_verification_and_rollback_evidence():
    result = collect_task_logs.parse_task_log_text(ZH_TASK_LOG)

    assert [v.verification_type for v in result.verifications] == ['unit', 'not verified']
    assert result.verifications[0].claim == 'parser extracts user requests and AI decisions.'
    assert 'pytest tests/test_collect_task_logs.py' in result.verifications[0].raw_evidence
    assert len(result.rollbacks) == 1
    assert result.rollbacks[0].failure_scenario == 'v0.5 digest confuses the user.'
    assert result.rollbacks[0].verified_rollback == 'partial'


def test_placeholder_sections_are_not_counted_as_evidence():
    result = collect_task_logs.parse_task_log_text(PLACEHOLDER_TASK_LOG, source='placeholder.md')

    assert result.user_requests == []
    assert result.ai_decisions == []
    assert result.verifications == []
    assert result.has_evidence is False
    assert any('placeholder' in warning.lower() for warning in result.warnings)


def test_malformed_log_returns_warning_not_exception():
    result = collect_task_logs.parse_task_log_text('not a task log at all', source='bad.md')

    assert result.source == 'bad.md'
    assert result.has_evidence is False
    assert result.user_requests == []
    assert result.ai_decisions == []
    assert any('missing' in warning.lower() for warning in result.warnings)


def test_collect_task_logs_reads_markdown_files_from_directory(tmp_path):
    log_dir = tmp_path / 'logs' / 'tasks'
    log_dir.mkdir(parents=True)
    (log_dir / '2026-06-05-v05.md').write_text(ZH_TASK_LOG, encoding='utf-8')
    (log_dir / 'ignore.txt').write_text(ZH_TASK_LOG, encoding='utf-8')

    results = collect_task_logs.collect_task_logs(log_dir)

    assert len(results) == 1
    assert results[0].source.endswith('2026-06-05-v05.md')
    assert results[0].has_evidence is True


def test_collect_task_logs_filters_by_metadata_date(tmp_path):
    old_log = ZH_TASK_LOG.replace('- Date: 2026-06-05', '- Date: 2026-06-04').replace(
        '使用者說「繼續」，接續 v0.5。',
        'OLD REQUEST should not appear',
    )
    (tmp_path / 'today.md').write_text(ZH_TASK_LOG, encoding='utf-8')
    (tmp_path / 'old.md').write_text(old_log, encoding='utf-8')

    results = collect_task_logs.collect_task_logs(tmp_path, date='2026-06-05')

    assert len(results) == 1
    assert results[0].metadata['Date'] == '2026-06-05'
    assert 'OLD REQUEST should not appear' not in '\n'.join(results[0].user_requests)


def test_collect_task_logs_filters_by_filename_date_when_metadata_missing(tmp_path):
    no_metadata = ZH_TASK_LOG.replace(
        '## Metadata\n\n- Date: 2026-06-05\n- Actor: Example Agent\n- Repo: ai-development-control-log\n- Branch: feat/v0.5-task-control-log\n- Commit / PR: pending\n',
        '## Metadata\n\n',
    )
    (tmp_path / '2026-06-05-task.md').write_text(no_metadata, encoding='utf-8')
    (tmp_path / '2026-06-04-task.md').write_text(
        no_metadata.replace('使用者說「繼續」，接續 v0.5。', 'OLD REQUEST should not appear'),
        encoding='utf-8',
    )

    results = collect_task_logs.collect_task_logs(tmp_path, date='2026-06-05')

    assert len(results) == 1
    assert results[0].source.endswith('2026-06-05-task.md')


def test_parse_task_log_redacts_secret_values():
    hooks_host = 'hooks.' + 'slack.com'
    feishu_host = 'open.' + 'feishu.cn'
    openai_prefix = 's' + 'k-'
    slack_prefix = 'xo' + 'xb-'
    secrets = [
        f'https://{hooks_host}/services/T000/B000/FAKE_SECRET_SHOULD_NOT_APPEAR',
        f'https://{feishu_host}/open-apis/bot/v2/hook/FAKE_SECRET_SHOULD_NOT_APPEAR',
        '123456789:' + 'A' * 35,
        openai_prefix + 'FAKEKEYSHOULDNOTAPPEAR1234567890',
        slack_prefix + 'FAKE_SLACK_TOKEN_SHOULD_NOT_APPEAR-1234567890abcdef',
        'Authorization: Bearer FAKE_B...ef',
        'API' + '_KEY=FAKE_API_KEY_SHOULD_NOT_APPEAR_1234567890abcdef',
    ]
    evidence = ' && '.join(secrets)

    text = ZH_TASK_LOG.replace(
        'python -m pytest tests/test_collect_task_logs.py -q',
        f'env SLACK_WEBHOOK_URL={evidence} python scripts/send_daily_digest.py digest.md --provider slack',
    ).replace(
        'use v0.4.1 release tag or remove --task-log-dir.',
        f'Call {evidence} again to rollback.',
    )

    result = collect_task_logs.parse_task_log_text(text, source='task.md')
    rendered = repr(result)

    for secret in secrets:
        assert secret not in rendered
    assert '[REDACTED]' in rendered
