#!/usr/bin/env python3
"""Build a readable Daily AI Decision Digest from local git activity.

This script is intentionally rule-based. It does not ask an LLM to
summarize itself. The output is conservative: when it cannot know whether
a commit was user-requested or AI-decided, it says so plainly.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Iterable

from collect_task_logs import TaskLogParseResult, collect_task_logs


@dataclass(frozen=True)
class CommitInfo:
    sha: str
    author: str
    date: str
    subject: str


@dataclass(frozen=True)
class DailyActivity:
    commits: list[CommitInfo]
    touched_paths: list[str]
    since: str
    until: str


HIGH_RISK_PATTERNS = [
    re.compile(r'(^|/)(migrations?|schema|prisma|supabase|database|db)(/|$)', re.I),
    re.compile(r'(^|/)(auth|oauth|login|session|permission|policy|roles?)(/|$)', re.I),
    re.compile(r'(payment|billing|stripe|invoice|subscription|checkout)', re.I),
    re.compile(r'(deploy|production|prod|gateway|webhook|worker|cron)', re.I),
    re.compile(r'(^|/)(\.env|secrets?|credentials?|tokens?)(\.|/|$)', re.I),
    re.compile(r'(^|/)\.github/workflows/', re.I),
]


def detect_high_risk_paths(paths: Iterable[str]) -> list[str]:
    """Return paths that look like high-risk AI-control touchpoints."""
    risky: list[str] = []
    for path in paths:
        if any(pattern.search(path) for pattern in HIGH_RISK_PATTERNS):
            risky.append(path)
    return sorted(dict.fromkeys(risky))


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ['git', *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def collect_git_activity(root: Path, since: str, until: str) -> DailyActivity:
    """Collect commits and touched paths for the digest window."""
    log = _run_git(
        [
            'log',
            f'--since={since}',
            f'--until={until}',
            '--pretty=format:%h%x1f%an%x1f%cI%x1f%s',
        ],
        root,
    )
    commits: list[CommitInfo] = []
    for line in log.stdout.splitlines():
        parts = line.split('\x1f', 3)
        if len(parts) != 4:
            continue
        commits.append(CommitInfo(*parts))

    touched_paths: list[str] = []
    if commits:
        # commits are newest-first from git log. Diff oldest^..newest to collect paths.
        newest = commits[0].sha
        oldest = commits[-1].sha
        diff = _run_git(['diff', '--name-only', f'{oldest}^', newest], root)
        if diff.returncode == 0:
            touched_paths = [p for p in diff.stdout.splitlines() if p.strip()]
        else:
            # Root-commit fallback: union per-commit changed files.
            seen: set[str] = set()
            for c in commits:
                show = _run_git(['show', '--pretty=format:', '--name-only', c.sha], root)
                for p in show.stdout.splitlines():
                    if p.strip():
                        seen.add(p.strip())
            touched_paths = sorted(seen)

    return DailyActivity(
        commits=commits,
        touched_paths=sorted(dict.fromkeys(touched_paths)),
        since=since,
        until=until,
    )


def _bullet_lines(items: Iterable[str], empty: str, limit: int = 12) -> str:
    items = list(items)
    if not items:
        return f'- {empty}'
    shown = items[:limit]
    lines = [f'- {item}' for item in shown]
    if len(items) > limit:
        lines.append(f'- …另有 {len(items) - limit} 筆，請看 workflow artifact。')
    return '\n'.join(lines)


def _commit_lines(commits: list[CommitInfo]) -> str:
    if not commits:
        return '- 沒有新的 commit。人話：這個 repo 昨天沒有留下任何可審核的程式改動證據。'
    return '\n'.join(
        f'- `{c.sha}` — {c.subject}（{c.author}，{c.date}）'
        for c in commits[:12]
    ) + (f'\n- …另有 {len(commits) - 12} 個 commit。' if len(commits) > 12 else '')


def _usable_task_logs(task_logs: list[TaskLogParseResult] | None) -> list[TaskLogParseResult]:
    return [log for log in (task_logs or []) if log.has_evidence]


def _source_label(log: TaskLogParseResult) -> str:
    return Path(log.source).name if log.source else 'task log'


def _limit_lines(lines: list[str], limit: int = 12) -> str:
    if not lines:
        return ''
    shown = lines[:limit]
    if len(lines) > limit:
        shown.append(f'- …另有 {len(lines) - limit} 筆 task-log evidence。')
    return '\n'.join(shown)


def _render_user_requests(task_logs: list[TaskLogParseResult] | None) -> str:
    logs = _usable_task_logs(task_logs)
    lines = [
        f'- {request}（來源：{_source_label(log)}）'
        for log in logs
        for request in log.user_requests
    ]
    if lines:
        return _limit_lines(lines)
    return (
        '- 自動模式只能看到 git 證據，無法可靠判斷每個 commit 是不是人類明確要求。\n'
        '- 如果你要更準，請讓 agent 每次任務把「使用者明確要求」寫進 `logs/tasks/YYYY-MM-DD-<slug>.md`，可從 `templates/task-control-log.zh-TW.md` 或 `templates/task-control-log.en.md` 複製。'
    )


def _sentence(value: str) -> str:
    value = value.strip()
    if not value:
        return ''
    if value[-1] in '。.!！?？':
        return value
    return value + '。'


def _render_ai_decisions(task_logs: list[TaskLogParseResult] | None) -> str:
    logs = _usable_task_logs(task_logs)
    lines: list[str] = []
    for log in logs:
        for decision in log.ai_decisions:
            parts = [_sentence(decision.decision)]
            if decision.rationale:
                parts.append(f'理由：{decision.rationale}')
            if decision.should_have_asked_user_first:
                parts.append(f'是否應先問：{decision.should_have_asked_user_first}')
            lines.append(f'- {" ".join(parts)}（來源：{_source_label(log)}）')
    if lines:
        return _limit_lines(lines)
    return (
        '- 自動模式沒有從 commit 本身可靠讀到「AI 自己決定」清單。\n'
        '- 這是風險提醒：沒有記錄 ≠ 沒有自作主張。\n'
        '- 下一步應該由 agent 在任務結束時補上 `logs/tasks/YYYY-MM-DD-<slug>.md` task control log，這份 daily digest 才能更準。'
    )


def _render_deviations(task_logs: list[TaskLogParseResult] | None) -> str:
    logs = _usable_task_logs(task_logs)
    lines: list[str] = []
    for log in logs:
        for deviation in log.spec_deviations:
            detail = []
            if deviation.original_spec:
                detail.append(f'原規格：{deviation.original_spec}')
            if deviation.actual_implementation:
                detail.append(f'實際：{deviation.actual_implementation}')
            if deviation.reason:
                detail.append(f'原因：{deviation.reason}')
            if deviation.needs_user_confirmation:
                detail.append(f'需確認：{deviation.needs_user_confirmation}')
            suffix = f'（{"；".join(detail)}；來源：{_source_label(log)}）' if detail else f'（來源：{_source_label(log)}）'
            lines.append(f'- {deviation.deviation}{suffix}')
    if lines:
        return _limit_lines(lines)
    if logs:
        return '- task logs 沒有記錄偏離；若這不符合事實，請修正該 task log。'
    return (
        '- 自動模式沒有偵測到明確偏離規格的證據。\n'
        '- 但這只代表 git commit / 檔名沒有足夠證據，不代表完全沒有偏離。\n'
        '- 如果今天有 PR，請一起看 PR 描述和 review comment。'
    )


def _render_risk_touchpoints(risky_paths: str, task_logs: list[TaskLogParseResult] | None) -> str:
    logs = _usable_task_logs(task_logs)
    lines: list[str] = []
    for log in logs:
        for touchpoint in log.high_risk_touchpoints:
            detail = []
            if touchpoint.risk_type:
                detail.append(f'風險：{touchpoint.risk_type}')
            if touchpoint.user_confirmed:
                detail.append(f'使用者確認：{touchpoint.user_confirmed}')
            if touchpoint.rollback_path:
                detail.append(f'退路：{touchpoint.rollback_path}')
            suffix = f'（{"；".join(detail)}；來源：{_source_label(log)}）' if detail else f'（來源：{_source_label(log)}）'
            lines.append(f'- {touchpoint.path_or_operation}{suffix}')
    if lines:
        return _limit_lines(lines) + '\n\n檔名規則掃描也看到：\n\n' + risky_paths
    return risky_paths


def _render_verifications(task_logs: list[TaskLogParseResult] | None) -> str:
    logs = _usable_task_logs(task_logs)
    lines: list[str] = []
    for log in logs:
        for verification in log.verifications:
            evidence = f' 證據：{verification.raw_evidence}' if verification.raw_evidence else ''
            kind = f' 類型：{verification.verification_type}' if verification.verification_type else ''
            lines.append(f'- {verification.claim}。{kind}{evidence}（來源：{_source_label(log)}）')
    base = [
        '- 已驗證：這份 digest 的 7 個問題結構完整，可以被 `scripts/validate_daily_digest.py` 檢查。',
        '- 已驗證：workflow 會再跑 repo validator 與 pytest。',
        '- 沒驗證：production 是否正常。',
    ]
    if lines:
        return _limit_lines(lines) + '\n' + '\n'.join(base)
    return '\n'.join(base + [
        '- 沒驗證：每個 commit 背後是不是真的由使用者要求。',
        '- 沒驗證：外部配送是否成功，除非 delivery provider 已設定且 workflow log 顯示成功。',
    ])


def _render_rollbacks(task_logs: list[TaskLogParseResult] | None, fallback: str) -> str:
    logs = _usable_task_logs(task_logs)
    lines: list[str] = []
    for log in logs:
        for rollback in log.rollbacks:
            detail = []
            if rollback.rollback_procedure:
                detail.append(f'退路：{rollback.rollback_procedure}')
            if rollback.verified_rollback:
                detail.append(f'已驗證可退：{rollback.verified_rollback}')
            suffix = f'（{"；".join(detail)}；來源：{_source_label(log)}）' if detail else f'（來源：{_source_label(log)}）'
            lines.append(f'- {rollback.failure_scenario}{suffix}')
    generic = [
        f'- 程式碼回退：{fallback}',
        '- 報告寄錯：把 repo variable `DELIVERY_PROVIDER` 改成 `none`，或刪除對應 webhook secret。',
        '- 高風險檔案被動到：先不要繼續 deploy，請人看 §5 的高風險路徑。',
    ]
    if lines:
        return _limit_lines(lines) + '\n' + '\n'.join(generic)
    return '\n'.join(generic)


def render_digest(
    date: str,
    activity: DailyActivity,
    timezone: str = 'UTC',
    task_logs: list[TaskLogParseResult] | None = None,
) -> str:
    """Render a zh-TW digest that passes validate_daily_digest.py."""
    commit_count = len(activity.commits)
    risk_paths = detect_high_risk_paths(activity.touched_paths)
    risk_status = '有高風險路徑，需要人看' if risk_paths else '0 件'
    commit_summary = f'{commit_count} 個 commit' if commit_count else '沒有新的 commit'
    action_line = (
        f'要看：{commit_summary}；先看「高風險操作」與「AI 自己決定」。'
        if commit_count or risk_paths
        else '不用處理：今天沒有新的 repo 改動，也沒有偵測到高風險路徑。'
    )
    decision_line = (
        '需要人工判斷。'
        if commit_count or risk_paths
        else '今天沒有可判斷的新決策。'
    )
    evidence_line = (
        '證據：GitHub 近 24 小時 commit / 改動檔案 / task logs。'
        if commit_count or risk_paths
        else '證據：GitHub 近 24 小時沒有新的 commit。'
    )
    next_action = (
        '檢查下方 §3/§5，再決定要不要介入。'
        if commit_count or risk_paths
        else '不用點開細看；除非你昨天其實有要求 AI 做事，但這裡沒記到。'
    )
    rollback_line = (
        f'如需回退，先看 commit 範圍，再用 `git revert` 逐筆回退；最新 commit 是 `{activity.commits[0].sha}`。'
        if activity.commits
        else '沒有新的 commit，通常不需要回退。若外部服務有異常，先停用 delivery provider。'
    )

    changed_paths = _bullet_lines(
        activity.touched_paths,
        '沒有偵測到改動檔案。',
    )
    risky_paths = _bullet_lines(
        risk_paths,
        '未偵測到 DB / 金流 / 權限 / production / workflow 類高風險路徑。',
    )

    return f"""# 每日 AI 決策摘要 — {date}

## 📋 0. 1 分鐘版（給老闆看）

- 結論：{action_line}
- AI 決策重點：{decision_line}
- 高風險操作：{risk_status}。
- 你要做什麼：{next_action}
- {evidence_line}

## 1. AI 做了什麼？

{_commit_lines(activity.commits)}

改動檔案：

{changed_paths}

## 2. 哪些是你明確要求的？

{_render_user_requests(task_logs)}

## 3. 哪些是 AI 自己決定的？

{_render_ai_decisions(task_logs)}

## 4. 偏離原本規格了嗎？

{_render_deviations(task_logs)}

## 5. 有沒有碰到高風險操作？

{_render_risk_touchpoints(risky_paths, task_logs)}

判斷方式：優先讀取 task-level control logs；同時掃描檔名是否碰到 DB migration、auth、金流、production、workflow、secret、webhook 等關鍵字。

## 6. 驗證了什麼？沒驗證什麼？

{_render_verifications(task_logs)}

## 7. 出事怎麼退？

{_render_rollbacks(task_logs, rollback_line)}

## 8. 這份 digest 你看得懂嗎？

請回覆：

- ✅ 看得懂，可以每天收。
- ⚠️ 大致懂，但有一段太技術。
- ❌ 看不懂，請 agent 下次改短、改白話。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a daily AI decision digest from git activity.')
    parser.add_argument('--output', required=True, help='Output markdown path.')
    parser.add_argument('--date', required=True, help='Digest date, e.g. 2026-06-05.')
    parser.add_argument('--since', default='24 hours ago', help='git log --since window.')
    parser.add_argument('--until', default='now', help='git log --until window.')
    parser.add_argument('--timezone', default='Asia/Taipei', help='Reader timezone label.')
    parser.add_argument('--root', default='.', help='Repository root.')
    parser.add_argument(
        '--task-log-dir',
        default='logs/tasks',
        help='Directory containing v0.5 task-level control logs. Relative paths resolve under --root.',
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    task_log_dir = Path(args.task_log_dir)
    if not task_log_dir.is_absolute():
        task_log_dir = root / task_log_dir
    task_logs = collect_task_logs(task_log_dir, date=args.date)
    activity = collect_git_activity(root, since=args.since, until=args.until)
    text = render_digest(args.date, activity, timezone=args.timezone, task_logs=task_logs)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding='utf-8')
    print(f'Wrote digest: {out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
