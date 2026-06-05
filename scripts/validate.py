#!/usr/bin/env python3
"""Lightweight repository validation for AI Development Control Log."""
import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'README.md',
    'README.zh-CN.md',
    'README.en.md',
    'CLAUDE.md',
    '.cursor/rules/ai-development-control-log.mdc',
    'skills/ai-development-control-log/SKILL.md',
    'templates/implementation-control-log.md',
    'templates/implementation-control-log.zh-TW.md',
    'templates/irreversible-operations-checklist.md',
    'examples/calc-feature-control-log.md',
    'examples/billing-change-control-log.md',
    'examples/database-migration-control-log.md',
    'examples/multi-round-control-log.md',
    'articles/manage-ai-engineer-with-control-log.md',
    'examples/agent-decision-digest.example.md',
    'templates/daily-decision-digest.zh-TW.md',
    'templates/daily-decision-digest.en.md',
    'examples/daily-decision-digest.zh-TW.md',
    'examples/daily-decision-digest.en.md',
    'examples/language-selection-control-log.zh-TW.md',
    'docs/automation/optional-delivery-automation.md',
    'templates/daily-digest-delivery-config.zh-TW.md',
    'templates/daily-digest-delivery-config.en.md',
    'examples/github-actions-daily-digest.yml',
    'examples/hermes-cron-daily-digest.zh-TW.md',
    # v0.4 daily digest upgrade — real, runnable workflow + new validator
    '.github/workflows/daily-digest.yml',
    'scripts/build_daily_digest.py',
    'scripts/send_daily_digest.py',
    'scripts/validate_daily_digest.py',
    'docs/install/agent-assisted-install.zh-TW.md',
    'docs/install/agent-assisted-install.en.md',
    'docs/install/agent-assisted-install.zh-CN.md',
    'templates/agent-install-prompt.zh-TW.md',
    'templates/agent-install-prompt.en.md',
    'templates/agent-install-prompt.zh-CN.md',
    # v0.5 task-level control logs — evidence source for daily digest
    'templates/task-control-log.zh-TW.md',
    'templates/task-control-log.en.md',
    'examples/task-control-log-agent-install-v0.5.zh-TW.md',
    'docs/automation/task-level-control-log-v0.5.md',
    'docs/plans/v0.5-task-level-control-log-plan.md',
    'scripts/collect_task_logs.py',
    # v0.2 Evidence Layer
    'templates/implementation-control-log.v0.2.md',
    'templates/implementation-control-log.zh-TW.v0.2.md',
    'examples/billing-change-control-log.v0.2.md',
    'docs/automation/evidence-layer-v0.2.md',
    'scripts/collect_evidence.py',
    'scripts/collect_evidence.sh',
    # v0.3 Replit-proof
    'templates/implementation-control-log.v0.3.md',
    'templates/implementation-control-log.zh-TW.v0.3.md',
    'examples/billing-change-control-log.v0.3.md',
    'docs/automation/evidence-layer-v0.3.md',
    'scripts/collect_rollback_evidence.py',
    'scripts/detect_high_risk_touchpoints.py',
    'config/high_risk_patterns.yml',
    # v0.3.1 Actor metadata
    'templates/implementation-control-log.v0.3.1.md',
    'templates/implementation-control-log.zh-TW.v0.3.1.md',
    'examples/billing-change-control-log.v0.3.1.md',
    'docs/automation/evidence-layer-v0.3.1.md',
    'scripts/collect_actor_metadata.py',
]

REPO_ONLY_REQUIRED: list[str] = []

VALIDATION_MODES = ('repo', 'kit', 'strict')

DAILY_DIGEST_FILES = [
    'templates/daily-decision-digest.zh-TW.md',
    'templates/daily-decision-digest.en.md',
    'examples/daily-decision-digest.zh-TW.md',
    'examples/daily-decision-digest.en.md',
]

# v0.4: the digest must answer all 7 user-facing questions
# (plus the 1-minute summary block, which is checked by
# scripts/validate_daily_digest.py).
#
# The main validator checks a *compact* subset of headings per file
# (zh-TW for zh-TW files, en for en files). The deeper "all 7
# questions answered" check with the 1-minute block is in
# scripts/validate_daily_digest.py.
REQUIRED_DAILY_DIGEST_HEADINGS_ZH_TW = [
    '語言與讀者設定',
    'AI 做了什麼？',
    '哪些是你明確要求的？',
    '哪些是 AI 自己決定的？',
    '偏離原本規格了嗎？',
    '有沒有碰到高風險操作？',
    '驗證了什麼？沒驗證什麼？',
    '出事怎麼退？',
    '這份 digest 你看得懂嗎？',
]

REQUIRED_DAILY_DIGEST_HEADINGS_EN = [
    'Language and Audience',
    'What did AI do?',
    'What did the user explicitly require?',
    'What did AI decide on its own?',
    'Did it deviate from the spec?',
    'Did it touch any high-risk operation?',
    'What was verified? What was not?',
    'If it breaks, how do you roll back?',
    'Can you read this digest?',
]

REQUIRED_DAILY_DIGEST_HEADINGS = (
    REQUIRED_DAILY_DIGEST_HEADINGS_ZH_TW + REQUIRED_DAILY_DIGEST_HEADINGS_EN
)

DELIVERY_AUTOMATION_FILES = [
    'docs/automation/optional-delivery-automation.md',
    'templates/daily-digest-delivery-config.zh-TW.md',
    'examples/hermes-cron-daily-digest.zh-TW.md',
]

REQUIRED_DELIVERY_AUTOMATION_HEADINGS = [
    '自動寄送是選配，不是預設',
    '寄送通道',
    '安全 gate',
    '驗證證據',
    '回滾方式',
]

TASK_CONTROL_LOG_FILES = [
    'templates/task-control-log.zh-TW.md',
    'templates/task-control-log.en.md',
    'examples/task-control-log-agent-install-v0.5.zh-TW.md',
]

REQUIRED_TASK_CONTROL_LOG_HEADINGS = [
    'Metadata',
    'User explicitly asked',
    'AI self-decided',
    'Spec deviations',
    'High-risk touchpoints',
    'Verification evidence',
    'Rollback evidence',
    'Human-readable final summary',
]

REQUIRED_V05_DOC_HEADINGS = [
    'Why v0.5',
    'What changes in v0.5',
    'How agents should use v0.5',
    'What v0.5 does NOT do',
    'Evidence rules',
    'Migration from v0.4.1',
]

REQUIRED_TEMPLATE_HEADINGS = [
    '語言與讀者設定',
    'Task Goal',
    'Timeline',
    'Explicit User Requirements',
    'Open Questions and Assumptions',
    'AI-Made Decisions',
    'Spec Deviations',
    'Surgical Change Traceability',
    'High-Risk / Irreversible Operation Check',
    'Verification Results',
    'Rollback Plan',
]

REQUIRED_ZH_TW_TEMPLATE_HEADINGS = [
    '語言與讀者設定',
    '任務目標',
    '時間軸',
    '使用者明確要求',
    '待釐清問題與假設',
    'AI 自行決定',
    '規格偏離',
    'Surgical Change 追溯',
    '取捨',
    '高風險 / 不可逆操作檢查',
    '驗證結果',
    '回滾計畫',
    '給人類審查的最終摘要',
]

# v0.2 templates add the Evidence Layer (9.5) with seven sub-blocks.
REQUIRED_V02_TEMPLATE_HEADINGS = [
    '語言與讀者設定',
    'Task Goal',
    'Explicit User Requirements',
    'Open Questions and Assumptions',
    'AI-Made Decisions',
    'Spec Deviations',
    'Surgical Change Traceability',
    'Tradeoffs',
    'High-Risk / Irreversible Operation Check',
    'Verification Results',
    '9.5.1 Changed Files',
    '9.5.2 Diff Summary',
    '9.5.3 Test Result',
    '9.5.4 Verification Type',
    '9.5.5 Commit Hash',
    '9.5.6 High-Risk Touchpoints',
    '9.5.7 Rollback Evidence',
    'Rollback Plan',
    'Final Summary for Human Review',
]

REQUIRED_V02_ZH_TW_TEMPLATE_HEADINGS = [
    '語言與讀者設定',
    '任務目標',
    '使用者明確要求',
    '待釐清問題與假設',
    'AI 自行決定',
    '規格偏離',
    'Surgical Change 追溯',
    '取捨',
    '高風險 / 不可逆操作檢查',
    '驗證結果',
    '9.5.1 改動檔案',
    '9.5.2 Diff 摘要',
    '9.5.3 測試結果',
    '9.5.4 驗證類型',
    '9.5.5 Commit Hash',
    '9.5.6 高風險接觸點',
    '9.5.7 回滾證據',
    '回滾計畫',
    '給人類審查的最終摘要',
]

REQUIRED_EVIDENCE_LAYER_HEADINGS = [
    'Why v0.2',
    'What changes in v0.2',
    'How to use v0.2',
    'What v0.2 does NOT do',
]

# v0.3 templates add the 0.5 Actor section and tighten 9.5.6 / 9.5.7.
REQUIRED_V03_TEMPLATE_HEADINGS = [
    '語言與讀者設定',
    'Task Goal',
    'Explicit User Requirements',
    'Open Questions and Assumptions',
    'AI-Made Decisions',
    'Spec Deviations',
    'Surgical Change Traceability',
    'Tradeoffs',
    'High-Risk / Irreversible Operation Check',
    'Verification Results',
    '9.5.1 Changed Files',
    '9.5.2 Diff Summary',
    '9.5.3 Test Result',
    '9.5.4 Verification Type',
    '9.5.5 Commit Hash',
    '9.5.6 High-Risk Touchpoints',
    '9.5.7 Rollback Evidence',
    'Rollback Plan',
    'Final Summary for Human Review',
]

REQUIRED_V03_ZH_TW_TEMPLATE_HEADINGS = [
    '語言與讀者設定',
    '任務目標',
    '使用者明確要求',
    '待釐清問題與假設',
    'AI 自行決定',
    '規格偏離',
    'Surgical Change 追溯',
    '取捨',
    '高風險 / 不可逆操作檢查',
    '驗證結果',
    '9.5.1 改動檔案',
    '9.5.2 Diff 摘要',
    '9.5.3 測試結果',
    '9.5.4 驗證類型',
    '9.5.5 Commit Hash',
    '9.5.6 高風險接觸點',
    '9.5.7 回滾證據',
    '回滾計畫',
    '給人類審查的最終摘要',
]

REQUIRED_V03_EVIDENCE_LAYER_HEADINGS = [
    'Why v0.3',
    'What changes in v0.3',
    'How to use v0.3',
    'What v0.3 does NOT do',
]

# v0.3.1 hard-requires the 0.5 Actor & Provenance block.
REQUIRED_V03_1_TEMPLATE_HEADINGS = [
    '語言與讀者設定',
    'Task Goal',
    'Actor & Provenance',
    'Explicit User Requirements',
    'Open Questions and Assumptions',
    'AI-Made Decisions',
    'Spec Deviations',
    'Surgical Change Traceability',
    'Tradeoffs',
    'High-Risk / Irreversible Operation Check',
    'Verification Results',
    '9.5.1 Changed Files',
    '9.5.2 Diff Summary',
    '9.5.3 Test Result',
    '9.5.4 Verification Type',
    '9.5.5 Commit Hash',
    '9.5.6 High-Risk Touchpoints',
    '9.5.7 Rollback Evidence',
    'Rollback Plan',
    'Final Summary for Human Review',
]

REQUIRED_V03_1_ZH_TW_TEMPLATE_HEADINGS = [
    '語言與讀者設定',
    '任務目標',
    'Actor & Provenance',
    '使用者明確要求',
    '待釐清問題與假設',
    'AI 自行決定',
    '規格偏離',
    'Surgical Change 追溯',
    '取捨',
    '高風險 / 不可逆操作檢查',
    '驗證結果',
    '9.5.1 改動檔案',
    '9.5.2 Diff 摘要',
    '9.5.3 測試結果',
    '9.5.4 驗證類型',
    '9.5.5 Commit Hash',
    '9.5.6 高風險接觸點',
    '9.5.7 回滾證據',
    '回滾計畫',
    '給人類審查的最終摘要',
]

REQUIRED_V03_1_EVIDENCE_LAYER_HEADINGS = [
    'Why v0.3.1',
    'What changes in v0.3.1',
    'How to use v0.3.1',
    'What v0.3.1 does NOT do',
]

# Categories in config/high_risk_patterns.yml that the v0.3.1
# self-approval rule cares about.
HIGH_RISK_CATEGORIES = frozenset({
    "db-schema",
    "payment",
    "auth",
    "secret",
    "production-config",
    "core-calculation",
    "external-side-effect",
})

REQUIRED_SKILL_FRONTMATTER_FIELDS = [
    'name:',
    'description:',
    'version:',
    'license:',
]


def has_markdown_heading(text: str, heading: str) -> bool:
    """Return True only when heading appears as an actual Markdown heading.

    Allows an optional numbering prefix before the heading
    (`1.`, `9.5.1`, `0.5`, `1.1.1`) — either with or without a
    trailing dot before the space — and an optional tail after it
    as long as the tail does not start with a lowercase letter
    that would merge into a new English word (so
    `9.5.5 Commit Hash / PR Link` matches `9.5.5 Commit Hash`,
    and `0.5 Actor & Provenance (v0.3.1 — required)` matches
    `Actor & Provenance`).
    """
    # Numbering prefix: one or more dot-separated numbers followed
    # by either a dot + space, or a space alone. The latter handles
    # `0.5 Section` as well as `0.5. Section`.
    prefix = r'(?:\d+(?:\.\d+)*\.?\s+)?'
    # Tail: optional. Allowed when it starts with one of these separators,
    # which never form a new English word with the heading.
    sep = r'[\s/\\\u2014\u2013\(&\uff08\uff5b\[\{]'
    tail = rf'(?:{sep}[^\n]*)?'
    pattern = re.compile(
        r'^#{2,6}\s+' + prefix + re.escape(heading) + tail + r'\s*$',
        re.MULTILINE,
    )
    return bool(pattern.search(text))


def frontmatter_value(frontmatter: str, field: str) -> str | None:
    """Return a simple YAML frontmatter scalar value, or None if missing."""
    field_name = field.rstrip(':')
    match = re.search(rf'^{re.escape(field_name)}:[ \t]*(.*)$', frontmatter, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def required_files_for_mode(mode: str) -> list[str]:
    """Return required files for validation mode."""
    if mode not in VALIDATION_MODES:
        raise ValueError(f'unknown validation mode: {mode}')
    if mode == 'kit':
        return [rel for rel in REQUIRED if rel not in REPO_ONLY_REQUIRED]
    return list(REQUIRED)


def validate_repository(root: Path = ROOT, mode: str = 'repo') -> list[str]:
    errors: list[str] = []

    required_files = required_files_for_mode(mode)
    for rel in required_files:
        path = root / rel
        if not path.exists():
            errors.append(f'missing: {rel}')
        elif not path.read_text(encoding='utf-8').strip():
            errors.append(f'empty: {rel}')

    skill = root / 'skills/ai-development-control-log/SKILL.md'
    if skill.exists():
        text = skill.read_text(encoding='utf-8')
        if not text.startswith('---\n'):
            errors.append('SKILL.md must start with frontmatter')
        if '\n---\n' not in text[4:]:
            errors.append('SKILL.md frontmatter must close with ---')
        else:
            frontmatter = text.split('---', 2)[1]
            for field in REQUIRED_SKILL_FRONTMATTER_FIELDS:
                value = frontmatter_value(frontmatter, field)
                if value is None:
                    errors.append(f'SKILL.md frontmatter missing {field}')
                elif not value:
                    errors.append(f'SKILL.md frontmatter missing value for {field}')

    log_template = root / 'templates/implementation-control-log.md'
    if log_template.exists():
        text = log_template.read_text(encoding='utf-8')
        for heading in REQUIRED_TEMPLATE_HEADINGS:
            if not has_markdown_heading(text, heading):
                errors.append(f'template missing section: {heading}')

    zh_tw_log_template = root / 'templates/implementation-control-log.zh-TW.md'
    if zh_tw_log_template.exists():
        text = zh_tw_log_template.read_text(encoding='utf-8')
        for heading in REQUIRED_ZH_TW_TEMPLATE_HEADINGS:
            if not has_markdown_heading(text, heading):
                errors.append(f'zh-TW template missing section: {heading}')

    for rel in DAILY_DIGEST_FILES:
        digest = root / rel
        if digest.exists():
            text = digest.read_text(encoding='utf-8')
            # Pick the heading list based on the file name: zh-TW files
            # get the zh-TW heading list, en files get the en list.
            if rel.endswith('.en.md'):
                heading_set = REQUIRED_DAILY_DIGEST_HEADINGS_EN
            else:
                heading_set = REQUIRED_DAILY_DIGEST_HEADINGS_ZH_TW
            for heading in heading_set:
                if not has_markdown_heading(text, heading):
                    errors.append(
                        f'daily digest missing section: {rel}: {heading}'
                    )

    for rel in DELIVERY_AUTOMATION_FILES:
        doc = root / rel
        if doc.exists():
            text = doc.read_text(encoding='utf-8')
            for heading in REQUIRED_DELIVERY_AUTOMATION_HEADINGS:
                if not has_markdown_heading(text, heading):
                    errors.append(f'delivery automation missing section: {rel}: {heading}')

    for rel in TASK_CONTROL_LOG_FILES:
        task_doc = root / rel
        if task_doc.exists():
            text = task_doc.read_text(encoding='utf-8')
            for heading in REQUIRED_TASK_CONTROL_LOG_HEADINGS:
                if not has_markdown_heading(text, heading):
                    errors.append(f'task control log missing section: {rel}: {heading}')

    v05_doc = root / 'docs/automation/task-level-control-log-v0.5.md'
    if v05_doc.exists():
        text = v05_doc.read_text(encoding='utf-8')
        for heading in REQUIRED_V05_DOC_HEADINGS:
            if not has_markdown_heading(text, heading):
                errors.append(f'v0.5 doc missing section: {heading}')

    v02_template = root / 'templates/implementation-control-log.v0.2.md'
    if v02_template.exists():
        text = v02_template.read_text(encoding='utf-8')
        for heading in REQUIRED_V02_TEMPLATE_HEADINGS:
            if not has_markdown_heading(text, heading):
                errors.append(f'v0.2 template missing section: {heading}')

    v02_zh_tw_template = root / 'templates/implementation-control-log.zh-TW.v0.2.md'
    if v02_zh_tw_template.exists():
        text = v02_zh_tw_template.read_text(encoding='utf-8')
        for heading in REQUIRED_V02_ZH_TW_TEMPLATE_HEADINGS:
            if not has_markdown_heading(text, heading):
                errors.append(f'v0.2 zh-TW template missing section: {heading}')

    evidence_doc = root / 'docs/automation/evidence-layer-v0.2.md'
    if evidence_doc.exists():
        text = evidence_doc.read_text(encoding='utf-8')
        for heading in REQUIRED_EVIDENCE_LAYER_HEADINGS:
            if not has_markdown_heading(text, heading):
                errors.append(f'evidence-layer doc missing section: {heading}')

    v03_template = root / 'templates/implementation-control-log.v0.3.md'
    if v03_template.exists():
        text = v03_template.read_text(encoding='utf-8')
        for heading in REQUIRED_V03_TEMPLATE_HEADINGS:
            if not has_markdown_heading(text, heading):
                errors.append(f'v0.3 template missing section: {heading}')
        errors.extend(validate_v0_3_evidence_columns(text))

    v03_zh_tw_template = root / 'templates/implementation-control-log.zh-TW.v0.3.md'
    if v03_zh_tw_template.exists():
        text = v03_zh_tw_template.read_text(encoding='utf-8')
        for heading in REQUIRED_V03_ZH_TW_TEMPLATE_HEADINGS:
            if not has_markdown_heading(text, heading):
                errors.append(f'v0.3 zh-TW template missing section: {heading}')
        errors.extend(validate_v0_3_evidence_columns(text))

    v03_evidence_doc = root / 'docs/automation/evidence-layer-v0.3.md'
    if v03_evidence_doc.exists():
        text = v03_evidence_doc.read_text(encoding='utf-8')
        for heading in REQUIRED_V03_EVIDENCE_LAYER_HEADINGS:
            if not has_markdown_heading(text, heading):
                errors.append(f'v0.3 evidence-layer doc missing section: {heading}')

    # v0.3.1 templates: same as v0.3 schema, plus the hard-required
    # 0.5 Actor & Provenance block. The actor-metadata gate is
    # applied to the .v0.3.1 files only — v0.3 templates still pass
    # under the v0.3 schema.
    #
    # Note: templates in `templates/` are placeholders and are
    # allowed to have empty 0.5 rows (the human fills them in).
    # We only enforce 0.5 row completeness for example logs and
    # for any non-template markdown that lives elsewhere in the
    # repo, so that the example demonstrates a complete log.
    v03_1_template = root / 'templates/implementation-control-log.v0.3.1.md'
    if v03_1_template.exists():
        text = v03_1_template.read_text(encoding='utf-8')
        for heading in REQUIRED_V03_1_TEMPLATE_HEADINGS:
            if not has_markdown_heading(text, heading):
                errors.append(f'v0.3.1 template missing section: {heading}')
        errors.extend(validate_v0_3_evidence_columns(text))
        # Templates may have empty 0.5 rows; do not gate here.

    v03_1_zh_tw_template = root / 'templates/implementation-control-log.zh-TW.v0.3.1.md'
    if v03_1_zh_tw_template.exists():
        text = v03_1_zh_tw_template.read_text(encoding='utf-8')
        for heading in REQUIRED_V03_1_ZH_TW_TEMPLATE_HEADINGS:
            if not has_markdown_heading(text, heading):
                errors.append(f'v0.3.1 zh-TW template missing section: {heading}')
        errors.extend(validate_v0_3_evidence_columns(text))
        # Templates may have empty 0.5 rows; do not gate here.

    v03_1_evidence_doc = root / 'docs/automation/evidence-layer-v0.3.1.md'
    if v03_1_evidence_doc.exists():
        text = v03_1_evidence_doc.read_text(encoding='utf-8')
        for heading in REQUIRED_V03_1_EVIDENCE_LAYER_HEADINGS:
            if not has_markdown_heading(text, heading):
                errors.append(f'v0.3.1 evidence-layer doc missing section: {heading}')

    # v0.3.1 example: must pass the FULL gate, including 0.5
    # row completeness and the self-approval rule. The example
    # exists to demonstrate a complete log, so a half-empty
    # 0.5 block fails validation.
    v03_1_example = root / 'examples/billing-change-control-log.v0.3.1.md'
    if v03_1_example.exists():
        text = v03_1_example.read_text(encoding='utf-8')
        errors.extend(validate_v0_3_1_actor_metadata(text))

    return errors


def _table_has_column(text: str, header_substring: str) -> bool:
    """Return True if any markdown pipe-table header line in `text`
    contains `header_substring` (case-insensitive)."""
    needle = header_substring.lower()
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|") or not s.endswith("|"):
            continue
        # The second line in a pipe table is the alignment row
        # (---|---|---:|...). We only consider header lines, which
        # are followed by such an alignment row within the next
        # two lines.
        if needle in s.lower():
            return True
    return False


def _all_field_value_rows(text: str) -> dict[str, str]:
    """Walk every pipe table in `text` and collect {first_col: second_col}.

    This is intentionally permissive: a v0.3.1 log's Section 0.5
    has a `Field | Value` table, but a wider markdown file may
    have many tables. We use the union and rely on the unique
    field names (`Agent model`, `Human approver`, etc.) to
    disambiguate. If two tables in the same file happen to use
    the same first-column key, the latter wins — this is a
    documentation smell, not a validation gap.
    """
    out: dict[str, str] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("|") and s.endswith("|"):
            # Confirm the next non-empty line is an alignment row.
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                align = lines[j].strip()
                if align.startswith("|") and align.endswith("|") and "---" in align:
                    # Walk the rows.
                    for row_line in lines[j + 1:]:
                        rs = row_line.strip()
                        if not (rs.startswith("|") and rs.endswith("|")):
                            break
                        cells = [c.strip() for c in rs.strip("|").split("|")]
                        if len(cells) >= 2:
                            out[cells[0]] = cells[1]
                    i = j + 1
                    continue
        i += 1
    return out


def _section_body(text: str, heading_substring: str) -> str:
    """Return the substring of `text` between the first heading line
    matching `heading_substring` and the next heading of equal or
    higher level. Used to scope table lookups to a single section
    (so we don't accidentally match a 9.5.6 table from a sibling
    log)."""
    needle = heading_substring.lower()
    lines = text.splitlines()
    start = None
    level = None
    for i, line in enumerate(lines):
        s = line.lstrip()
        if s.startswith("#"):
            # Determine heading level by leading # count.
            hashes = len(s) - len(s.lstrip("#"))
            if start is not None and hashes <= level:
                return "\n".join(lines[start:i])
            if needle in s.lower() and start is None:
                start = i
                level = hashes
    if start is None:
        return ""
    return "\n".join(lines[start:])


def validate_v0_3_1_actor_metadata(text: str) -> list[str]:
    """Enforce Section 0.5 Actor & Provenance rules for a v0.3.1 log.

    Rules:
      1. The 0.5 table must exist.
      2. Required rows: Agent model, Agent session, Human approver,
         Approval evidence, Wall clock start, Wall clock end.
      3. No value may be empty (a `<FILL BY HAND>` placeholder is
         treated as empty for English but explicitly allowed for
         zh-TW since the script uses `<由人類填寫>`; the gate then
         only fails on the corresponding English column because
         the v0.3.1 spec treats both as equivalent placeholders.
      4. If 9.5.6 contains a row whose Touchpoint type is one of
         the seven HIGH_RISK_CATEGORIES, then Human approver MUST
         NOT be `self-approved`.
      5. Wall clock end must be >= Wall clock start, when both
         parse as ISO-8601.
    """
    errors: list[str] = []

    section = _section_body(text, "Actor & Provenance")
    if not section:
        return ["v0.3.1 log: section 0.5 'Actor & Provenance' missing"]

    # The 0.5 table has a "Field | Value" layout, so first column is
    # the field name and second column is the value. We scan every
    # table in the section; the unique field names
    # (`Agent model`, `Human approver`, ...) disambiguate.
    field_values = _all_field_value_rows(section)

    required_keys = [
        "Agent model", "Agent session", "Human approver",
        "Approval evidence", "Wall clock start", "Wall clock end",
    ]
    for key in required_keys:
        if key not in field_values:
            errors.append(f"v0.3.1 0.5 missing row: {key}")
            continue
        value = field_values[key].strip()
        # Allow the two known autofill placeholders so the script
        # can emit them; reject any other empty string.
        if not value or value in {"<FILL BY HAND>", "<由人類填寫>"}:
            # An empty / placeholder is fine for the *human-side*
            # rows (Human approver, Approval evidence) BEFORE
            # review. The agent's job is to leave them. But the
            # *agent-side* rows must always be filled.
            if key in {"Human approver", "Approval evidence"}:
                continue
            errors.append(f"v0.3.1 0.5 row '{key}' is empty / unfilled")

    # Self-approval rule: 9.5.6 high-risk + self-approved approver
    # is forbidden. Look only at the 9.5.6 table in the 9.5
    # section, not at any sibling log. We re-derive the section
    # body here so this gate is self-contained.
    section_9_5 = _section_body(text, "9.5 Evidence Layer") or \
        _section_body(text, "證據層")
    if section_9_5:
        section_9_5_6 = _section_body(section_9_5, "9.5.6") or section_9_5
        rows_in_9_5_6 = _all_field_value_rows(section_9_5_6)
        # The 9.5.6 table is a multi-column table
        # (Path | Touchpoint type | Why | Notes). `_all_field_value_rows`
        # only returns {first_col: second_col}, so we instead walk
        section_9_5_6 = _section_body(section_9_5, "9.5.6") or section_9_5
        lines_9_5_6 = section_9_5_6.splitlines()
        high_risk_present = False
        i = 0
        while i < len(lines_9_5_6):
            s = lines_9_5_6[i].strip()
            if (s.startswith("|") and s.endswith("|")
                    and "touchpoint type" in s.lower()):
                # Found the 9.5.6 header. Walk rows.
                j = i + 1
                while j < len(lines_9_5_6) and not lines_9_5_6[j].strip():
                    j += 1
                # Skip alignment.
                if j < len(lines_9_5_6):
                    for row_line in lines_9_5_6[j + 1:]:
                        rs = row_line.strip()
                        if not (rs.startswith("|") and rs.endswith("|")):
                            break
                        cells = [c.strip() for c in rs.strip("|").split("|")]
                        # cells: [Path, Touchpoint type, Why, Notes (optional)]
                        if len(cells) >= 2 and cells[1] in HIGH_RISK_CATEGORIES:
                            high_risk_present = True
                            break
                break
            i += 1
        # Fallback: zh-TW (cells: [路徑, 接觸類型, 為什麼, 備註])
        if not high_risk_present:
            for row_line in lines_9_5_6:
                rs = row_line.strip()
                if not (rs.startswith("|") and rs.endswith("|")):
                    continue
                cells = [c.strip() for c in rs.strip("|").split("|")]
                if len(cells) >= 2 and cells[1] in HIGH_RISK_CATEGORIES:
                    high_risk_present = True
                    break

        approver = field_values.get("Human approver", "").strip().lower()
        if high_risk_present and approver in {"self-approved", ""}:
            errors.append(
                "v0.3.1 self-approval is forbidden when 9.5.6 has "
                "high-risk touchpoints. Set Human approver to a "
                "GitHub handle (e.g. @user)."
            )

    # Wall clock ordering
    start = field_values.get("Wall clock start", "").strip()
    end = field_values.get("Wall clock end", "").strip()
    if start and end:
        # Strict ISO-8601 check: both must be parseable. We use
        # datetime.fromisoformat for portability (it understands
        # 'Z' as UTC in 3.11+).
        import datetime as _dt
        try:
            s = _dt.datetime.fromisoformat(start.replace("Z", "+00:00"))
            e = _dt.datetime.fromisoformat(end.replace("Z", "+00:00"))
            if e < s:
                errors.append(
                    f"v0.3.1 0.5: Wall clock end ({end}) is before "
                    f"Wall clock start ({start})"
                )
        except ValueError:
            errors.append(
                f"v0.3.1 0.5: Wall clock start/end not valid ISO-8601 "
                f"({start!r}, {end!r})"
            )

    return errors


def validate_v0_3_evidence_columns(text: str) -> list[str]:
    """v0.3 templates and examples must have the new evidence columns
    in 9.5.6 (touchpoint type) and 9.5.7 (exit code / conflict
    markers). Without these columns, the v0.3 promises are
    unfalsifiable."""
    errors: list[str] = []
    if not _table_has_column(text, "Touchpoint type") and \
       not _table_has_column(text, "接觸類型"):
        errors.append(
            "v0.3 log: 9.5.6 table must include a 'Touchpoint type' / "
            "'接觸類型' column"
        )
    if not _table_has_column(text, "Exit code") and \
       not _table_has_column(text, "Exit code".lower()):
        errors.append(
            "v0.3 log: 9.5.7 table must include an 'Exit code' column"
        )
    if not _table_has_column(text, "Conflict markers") and \
       not _table_has_column(text, "Conflict markers"):
        errors.append(
            "v0.3 log: 9.5.7 table must include a 'Conflict markers' "
            "column"
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Validate the AI Development Control Log repository.')
    parser.add_argument(
        '--mode',
        choices=VALIDATION_MODES,
        default='repo',
        help='repo/strict require repository-maintainer artifacts; kit skips repo-only live logs for fork users.',
    )
    args = parser.parse_args(argv)

    errors = validate_repository(ROOT, mode=args.mode)
    if errors:
        print(f'VALIDATION FAILED ({args.mode} mode)')
        for error in errors:
            print('-', error)
        return 1

    print(f'VALIDATION PASSED ({args.mode} mode)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
