#!/usr/bin/env python3
"""Parse v0.5 task-level control logs.

The parser is intentionally conservative: it extracts only stable Markdown
sections and never invents evidence. Missing or placeholder-only sections
become warnings, not fatal errors, so the daily digest can fall back to git
evidence when task logs are absent or incomplete.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Iterable


@dataclass(frozen=True)
class TaskDecision:
    decision: str
    rationale: str = ''
    should_have_asked_user_first: str = ''


@dataclass(frozen=True)
class TaskDeviation:
    deviation: str
    original_spec: str = ''
    actual_implementation: str = ''
    reason: str = ''
    needs_user_confirmation: str = ''


@dataclass(frozen=True)
class TaskRiskTouchpoint:
    path_or_operation: str
    risk_type: str = ''
    user_confirmed: str = ''
    rollback_path: str = ''


@dataclass(frozen=True)
class TaskVerification:
    claim: str
    verification_type: str = ''
    raw_evidence: str = ''


@dataclass(frozen=True)
class TaskRollback:
    failure_scenario: str
    rollback_procedure: str = ''
    verified_rollback: str = ''


@dataclass(frozen=True)
class TaskLogParseResult:
    source: str
    metadata: dict[str, str] = field(default_factory=dict)
    user_requests: list[str] = field(default_factory=list)
    ai_decisions: list[TaskDecision] = field(default_factory=list)
    spec_deviations: list[TaskDeviation] = field(default_factory=list)
    high_risk_touchpoints: list[TaskRiskTouchpoint] = field(default_factory=list)
    verifications: list[TaskVerification] = field(default_factory=list)
    rollbacks: list[TaskRollback] = field(default_factory=list)
    final_summary: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def has_evidence(self) -> bool:
        return any([
            self.user_requests,
            self.ai_decisions,
            self.spec_deviations,
            self.high_risk_touchpoints,
            self.verifications,
            self.rollbacks,
            self.final_summary,
        ])


REQUIRED_SECTIONS = [
    'User explicitly asked',
    'AI self-decided',
    'Spec deviations',
    'High-risk touchpoints',
    'Verification evidence',
    'Rollback evidence',
]

PLACEHOLDER_MARKERS = (
    '...',
    '（填寫',
    '填寫',
    'todo',
    'tbd',
    'pending',
)

EMPTY_MARKERS = ('', 'none', 'n/a', 'na', '無', '沒有')

HEADING_RE = re.compile(r'^##\s+(.+?)\s*$', re.M)
DATE_RE = re.compile(r'(20\d{2}-\d{2}-\d{2})')
SECRET_PATTERNS = [
    re.compile(r'https://hooks\.slack\.com/services/[^\s)\]}>"\']+', re.I),
    re.compile(r'https://open\.feishu\.cn/open-apis/bot/v2/hook/[^\s)\]}>"\']+', re.I),
    re.compile(r'(?i)\bauthorization\s*:\s*bearer\s+[^\s)\]}>"\']+'),
    re.compile(r'(?i)\bbearer\s+[A-Za-z0-9._\-]{16,}\b'),
    re.compile(r'\b\d{6,}:[A-Za-z0-9_-]{20,}\b'),
    re.compile(r'\bsk-[A-Za-z0-9_\-]{16,}\b', re.I),
    re.compile(r'\bxox[baprs]-[A-Za-z0-9_\-]{16,}(?:-[A-Za-z0-9_\-]+)*\b', re.I),
    re.compile(r'\b(?:sk|xox[baprs]|gh[pousr]|github_pat)_[A-Za-z0-9_\-]{16,}\b', re.I),
    re.compile(r'(?i)\b(?:api[_-]?key|token|secret|password|webhook|authorization|bearer)\s*=\s*[^\s)\]}>"\']+'),
]


def redact_secrets(value: str) -> str:
    redacted = value
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub('[REDACTED]', redacted)
    return redacted


def _sections(text: str) -> dict[str, str]:
    matches = list(HEADING_RE.finditer(text))
    sections: dict[str, str] = {}
    for i, match in enumerate(matches):
        name = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[name] = text[start:end].strip()
    return sections


def _clean_value(value: str) -> str:
    return redact_secrets(value.strip())


def _strip_bullet(line: str) -> str:
    return re.sub(r'^\s*[-*]\s*', '', line).strip()


def _is_placeholder(value: str) -> bool:
    normalized = value.strip().strip('：:').strip().lower()
    if normalized in EMPTY_MARKERS:
        return True
    if any(marker in normalized for marker in PLACEHOLDER_MARKERS):
        return True
    return False


def _bullet_items(body: str) -> list[str]:
    items: list[str] = []
    for line in body.splitlines():
        if not re.match(r'^\s*[-*]\s+', line):
            continue
        value = _clean_value(_strip_bullet(line))
        if _is_placeholder(value):
            continue
        items.append(value)
    return items


def _metadata(body: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for item in _bullet_items(body):
        if ':' not in item:
            continue
        key, value = item.split(':', 1)
        value = value.strip()
        if value and not _is_placeholder(value):
            data[key.strip()] = value
    return data


def _entry_blocks(body: str, primary_label: str) -> list[dict[str, str]]:
    """Parse repeated bullet blocks like '- Decision: ...\n  Rationale: ...'."""
    blocks: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    current_key = ''
    primary_key = primary_label.lower()

    for raw_line in body.splitlines():
        if not raw_line.strip():
            continue
        bullet = re.match(r'^\s*[-*]\s+([^:]+):\s*(.*)$', raw_line)
        kv = re.match(r'^\s+([^:]+):\s*(.*)$', raw_line)
        continuation = re.match(r'^\s+(\S.*)$', raw_line)

        if bullet:
            label = bullet.group(1).strip().lower()
            value = _clean_value(bullet.group(2))
            if label == primary_key:
                if current:
                    blocks.append(current)
                current = {primary_key: value}
                current_key = primary_key
            else:
                if current is None:
                    current = {}
                current[label] = value
                current_key = label
            continue

        if kv and current is not None:
            label = kv.group(1).strip().lower()
            value = _clean_value(kv.group(2))
            current[label] = value
            current_key = label
            continue

        if continuation and current is not None and current_key:
            extra = _clean_value(continuation.group(1))
            if not extra:
                continue
            existing = current.get(current_key, '')
            current[current_key] = f'{existing} {extra}'.strip()

    if current:
        blocks.append(current)

    cleaned: list[dict[str, str]] = []
    for block in blocks:
        primary = block.get(primary_key, '')
        if _is_placeholder(primary):
            continue
        cleaned.append({k: v for k, v in block.items() if not _is_placeholder(v)})
    return cleaned


def _parse_decisions(body: str) -> list[TaskDecision]:
    return [
        TaskDecision(
            decision=b.get('decision', ''),
            rationale=b.get('rationale', ''),
            should_have_asked_user_first=b.get('should have asked user first', ''),
        )
        for b in _entry_blocks(body, 'Decision')
        if b.get('decision')
    ]


def _parse_deviations(body: str) -> list[TaskDeviation]:
    return [
        TaskDeviation(
            deviation=b.get('deviation', ''),
            original_spec=b.get('original spec', ''),
            actual_implementation=b.get('actual implementation', ''),
            reason=b.get('reason', ''),
            needs_user_confirmation=b.get('needs user confirmation', ''),
        )
        for b in _entry_blocks(body, 'Deviation')
        if b.get('deviation')
    ]


def _parse_touchpoints(body: str) -> list[TaskRiskTouchpoint]:
    return [
        TaskRiskTouchpoint(
            path_or_operation=b.get('path / operation', ''),
            risk_type=b.get('risk type', ''),
            user_confirmed=b.get('user confirmed', ''),
            rollback_path=b.get('rollback path', ''),
        )
        for b in _entry_blocks(body, 'Path / operation')
        if b.get('path / operation')
    ]


def _parse_verifications(body: str) -> list[TaskVerification]:
    return [
        TaskVerification(
            claim=b.get('claim', ''),
            verification_type=b.get('verification type', ''),
            raw_evidence=b.get('raw evidence', ''),
        )
        for b in _entry_blocks(body, 'Claim')
        if b.get('claim')
    ]


def _parse_rollbacks(body: str) -> list[TaskRollback]:
    return [
        TaskRollback(
            failure_scenario=b.get('failure scenario', ''),
            rollback_procedure=b.get('rollback command / toggle / procedure', ''),
            verified_rollback=b.get('verified rollback', ''),
        )
        for b in _entry_blocks(body, 'Failure scenario')
        if b.get('failure scenario')
    ]


def parse_task_log_text(text: str, source: str = '<memory>') -> TaskLogParseResult:
    sections = _sections(text)
    warnings: list[str] = []
    missing = [name for name in REQUIRED_SECTIONS if name not in sections]
    if missing:
        warnings.append(f'missing required sections: {", ".join(missing)}')

    user_requests = _bullet_items(sections.get('User explicitly asked', ''))
    ai_decisions = _parse_decisions(sections.get('AI self-decided', ''))
    spec_deviations = _parse_deviations(sections.get('Spec deviations', ''))
    touchpoints = _parse_touchpoints(sections.get('High-risk touchpoints', ''))
    verifications = _parse_verifications(sections.get('Verification evidence', ''))
    rollbacks = _parse_rollbacks(sections.get('Rollback evidence', ''))
    final_summary = _bullet_items(sections.get('Human-readable final summary', ''))

    if any(name in sections and not sections[name].strip() for name in REQUIRED_SECTIONS):
        warnings.append('one or more required sections are empty')

    if not any([user_requests, ai_decisions, spec_deviations, touchpoints, verifications, rollbacks, final_summary]):
        if sections:
            warnings.append('task log contains only placeholder or empty evidence')
        else:
            warnings.append('missing task-log markdown headings')

    return TaskLogParseResult(
        source=source,
        metadata=_metadata(sections.get('Metadata', '')),
        user_requests=user_requests,
        ai_decisions=ai_decisions,
        spec_deviations=spec_deviations,
        high_risk_touchpoints=touchpoints,
        verifications=verifications,
        rollbacks=rollbacks,
        final_summary=final_summary,
        warnings=warnings,
    )


def _result_date(result: TaskLogParseResult, path: Path) -> str:
    metadata_date = result.metadata.get('Date') or result.metadata.get('date')
    if metadata_date:
        match = DATE_RE.search(metadata_date)
        if match:
            return match.group(1)
    match = DATE_RE.search(path.name)
    if match:
        return match.group(1)
    return ''


def collect_task_logs(log_dir: Path | str, date: str | None = None) -> list[TaskLogParseResult]:
    root = Path(log_dir)
    if not root.exists() or not root.is_dir():
        return []
    results: list[TaskLogParseResult] = []
    for path in sorted(root.glob('*.md')):
        try:
            text = path.read_text(encoding='utf-8')
        except OSError as exc:
            result = TaskLogParseResult(source=str(path), warnings=[f'could not read task log: {exc.__class__.__name__}'])
            if date is None or _result_date(result, path) == date:
                results.append(result)
            continue
        result = parse_task_log_text(text, source=str(path))
        if date is not None and _result_date(result, path) != date:
            continue
        results.append(result)
    return results


def _print_summary(results: Iterable[TaskLogParseResult]) -> None:
    for result in results:
        status = 'evidence' if result.has_evidence else 'no-evidence'
        print(f'{result.source}: {status}; warnings={len(result.warnings)}')


def main() -> int:
    parser = argparse.ArgumentParser(description='Parse v0.5 task-level control logs.')
    parser.add_argument('log_dir', nargs='?', default='logs/tasks', help='Directory containing task log markdown files.')
    parser.add_argument('--date', help='Only include task logs for YYYY-MM-DD, using Metadata Date or filename date.')
    args = parser.parse_args()
    _print_summary(collect_task_logs(Path(args.log_dir), date=args.date))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
