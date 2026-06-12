"""Tests for build_daily_digest.py — daily digest generation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

import build_daily_digest  # noqa: E402
import validate_daily_digest  # noqa: E402


def _validate_rendered_digest(tmp_path: Path, text: str) -> list[str]:
    path = tmp_path / 'digest.md'
    path.write_text(text, encoding='utf-8')
    return validate_daily_digest.validate_digest(path)


def test_render_digest_with_no_activity_is_still_readable_and_valid(tmp_path):
    activity = build_daily_digest.DailyActivity(
        commits=[],
        touched_paths=[],
        since='24 hours ago',
        until='now',
    )

    text = build_daily_digest.render_digest(
        date='2026-06-05',
        activity=activity,
        timezone='Asia/Taipei',
    )

    assert '# 每日 AI 決策摘要 — 2026-06-05' in text
    assert '不用處理：今天沒有新的 repo 改動' in text
    assert '你要做什麼：不用點開細看' in text
    assert '沒有留下任何可審核的程式改動證據' in text
    assert _validate_rendered_digest(tmp_path, text) == []


def test_render_digest_lists_commits_and_high_risk_paths(tmp_path):
    activity = build_daily_digest.DailyActivity(
        commits=[
            build_daily_digest.CommitInfo(
                sha='abc1234',
                author='Example Agent',
                date='2026-06-05T08:00:00Z',
                subject='feat: add daily digest delivery',
            ),
            build_daily_digest.CommitInfo(
                sha='def5678',
                author='Example Agent',
                date='2026-06-05T09:00:00Z',
                subject='fix: validate rollback evidence',
            ),
        ],
        touched_paths=[
            '.github/workflows/daily-digest.yml',
            'db/migrations/001_add_users.sql',
            'scripts/send_daily_digest.py',
        ],
        since='24 hours ago',
        until='now',
    )

    text = build_daily_digest.render_digest(
        date='2026-06-05',
        activity=activity,
        timezone='Asia/Taipei',
    )

    assert '2 個 commit' in text
    assert 'feat: add daily digest delivery' in text
    assert 'db/migrations/001_add_users.sql' in text
    assert '高風險' in text
    assert _validate_rendered_digest(tmp_path, text) == []


def test_detect_high_risk_paths_flags_common_danger_zones():
    paths = [
        'README.md',
        'migrations/20260605_create_orders.sql',
        'src/auth/session.ts',
        '.github/workflows/deploy.yml',
        'config/payment.yml',
    ]

    risky = build_daily_digest.detect_high_risk_paths(paths)

    assert 'migrations/20260605_create_orders.sql' in risky
    assert 'src/auth/session.ts' in risky
    assert '.github/workflows/deploy.yml' in risky
    assert 'config/payment.yml' in risky
    assert 'README.md' not in risky
