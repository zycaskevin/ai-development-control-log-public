"""Tests for validate.py — repo protocol kit validator."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

import validate  # noqa: E402


# ---------------------------------------------------------------------------
# has_markdown_heading
# ---------------------------------------------------------------------------

def test_heading_basic():
    assert validate.has_markdown_heading('## Foo', 'Foo')
    assert validate.has_markdown_heading('### Foo', 'Foo')
    assert validate.has_markdown_heading('#### Foo', 'Foo')


def test_heading_with_number_prefix():
    assert validate.has_markdown_heading('## 1. Foo', 'Foo')
    assert validate.has_markdown_heading('### 9.5.1 Foo', '9.5.1 Foo')
    # '9.5.5 Commit Hash / PR Link' should still satisfy '9.5.5 Commit Hash'.
    assert validate.has_markdown_heading('### 9.5.5 Commit Hash / PR Link',
                                         '9.5.5 Commit Hash')


def test_heading_with_parenthesis():
    assert validate.has_markdown_heading('### 9.5.1 Foo (objective)',
                                         '9.5.1 Foo')


def test_heading_zh_tw():
    assert validate.has_markdown_heading('## 9.5.1 改動檔案（客觀）',
                                         '9.5.1 改動檔案')
    assert validate.has_markdown_heading('## 9.5.1 改動檔案',
                                         '9.5.1 改動檔案')


def test_heading_negative():
    # Different heading text should not match.
    assert not validate.has_markdown_heading('## Bar', 'Foo')
    # A heading that continues with another word should not match.
    assert not validate.has_markdown_heading('### 9.5.1 Commitment Issues',
                                             '9.5.1 Commit')
    # Plain text should not match.
    assert not validate.has_markdown_heading('Some Foo bar', 'Foo')
    # Empty string never matches.
    assert not validate.has_markdown_heading('', 'Foo')
    # h1 is intentionally excluded (we treat docs as ##+).
    assert not validate.has_markdown_heading('# Foo', 'Foo')


def test_heading_in_multiline_doc():
    text = (
        "# Title\n"
        "\n"
        "Some intro.\n"
        "\n"
        "## Section A\n"
        "\n"
        "### 9.5.1 Changed Files (objective)\n"
        "\n"
        "body\n"
    )
    assert validate.has_markdown_heading(text, '9.5.1 Changed Files')
    assert validate.has_markdown_heading(text, 'Section A')
    assert not validate.has_markdown_heading(text, 'Not Present')


# ---------------------------------------------------------------------------
# frontmatter_value
# ---------------------------------------------------------------------------

def test_frontmatter_value_present():
    fm = "name: foo\nversion: 0.2\nlicense: MIT\n"
    assert validate.frontmatter_value(fm, 'name:') == 'foo'
    assert validate.frontmatter_value(fm, 'version:') == '0.2'
    assert validate.frontmatter_value(fm, 'license:') == 'MIT'


def test_frontmatter_value_missing_returns_none():
    fm = "name: foo\n"
    assert validate.frontmatter_value(fm, 'description:') is None


def test_frontmatter_value_empty_value():
    # An empty value is a separate signal than a missing key.
    fm = "name: foo\ndescription:\n"
    assert validate.frontmatter_value(fm, 'description:') == ''


# ---------------------------------------------------------------------------
# required_files_for_mode
# ---------------------------------------------------------------------------

def test_required_files_for_mode_unknown():
    with pytest.raises(ValueError):
        validate.required_files_for_mode('nope')


def test_required_files_for_mode_includes_public_safe_digest_example():
    kit = validate.required_files_for_mode('kit')
    repo = validate.required_files_for_mode('repo')
    assert 'examples/agent-decision-digest.example.md' in repo
    assert 'examples/agent-decision-digest.example.md' in kit
    assert all(not rel.startswith('logs/') for rel in repo)
    assert all(not rel.startswith('logs/') for rel in kit)
    # Every kit file must also be in repo mode (kit is a strict subset or equal set).
    assert set(kit).issubset(set(repo))


def test_required_files_include_v05_task_log_assets():
    repo = validate.required_files_for_mode('repo')

    assert 'templates/task-control-log.zh-TW.md' in repo
    assert 'templates/task-control-log.en.md' in repo
    assert 'examples/task-control-log-agent-install-v0.5.zh-TW.md' in repo
    assert 'docs/automation/task-level-control-log-v0.5.md' in repo
    assert 'scripts/collect_task_logs.py' in repo


# ---------------------------------------------------------------------------
# validate_repository — boundary cases on a tmp_path fixture
# ---------------------------------------------------------------------------

def _write(root: Path, rel: str, body: str = 'x') -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding='utf-8')


def _minimal_repo(root: Path) -> None:
    """Create the minimal required file set so validate_repository passes."""
    for rel in validate.REQUIRED:
        _write(root, rel, 'placeholder content\n')
    # Skill needs a real frontmatter block to pass the SKILL.md check.
    _write(root, 'skills/ai-development-control-log/SKILL.md',
           "---\nname: foo\ndescription: bar\nversion: 0.1\n"
           "license: MIT\n---\nbody\n")
    # Templates need their required headings.
    for tmpl_rel, headings in [
        ('templates/implementation-control-log.md',
         validate.REQUIRED_TEMPLATE_HEADINGS),
        ('templates/implementation-control-log.zh-TW.md',
         validate.REQUIRED_ZH_TW_TEMPLATE_HEADINGS),
    ]:
        _write(root, tmpl_rel,
               '\n'.join(f'## {h}' for h in headings) + '\n')
    # Daily digest and delivery automation check against three files each.
    # v0.4: pick the per-language heading set so the fixture is valid
    # for the file we are about to create.
    for tmpl_rel, headings in [
        ('templates/daily-decision-digest.zh-TW.md',
         validate.REQUIRED_DAILY_DIGEST_HEADINGS_ZH_TW),
        ('examples/daily-decision-digest.zh-TW.md',
         validate.REQUIRED_DAILY_DIGEST_HEADINGS_ZH_TW),
        ('templates/daily-decision-digest.en.md',
         validate.REQUIRED_DAILY_DIGEST_HEADINGS_EN),
        ('examples/daily-decision-digest.en.md',
         validate.REQUIRED_DAILY_DIGEST_HEADINGS_EN),
        ('docs/automation/optional-delivery-automation.md',
         validate.REQUIRED_DELIVERY_AUTOMATION_HEADINGS),
        ('templates/daily-digest-delivery-config.zh-TW.md',
         validate.REQUIRED_DELIVERY_AUTOMATION_HEADINGS),
        ('examples/hermes-cron-daily-digest.zh-TW.md',
         validate.REQUIRED_DELIVERY_AUTOMATION_HEADINGS),
    ]:
        _write(root, tmpl_rel,
               '\n'.join(f'## {h}' for h in headings) + '\n')
    # v0.2 templates
    for tmpl_rel, headings in [
        ('templates/implementation-control-log.v0.2.md',
         validate.REQUIRED_V02_TEMPLATE_HEADINGS),
        ('templates/implementation-control-log.zh-TW.v0.2.md',
         validate.REQUIRED_V02_ZH_TW_TEMPLATE_HEADINGS),
        ('docs/automation/evidence-layer-v0.2.md',
         validate.REQUIRED_EVIDENCE_LAYER_HEADINGS),
    ]:
        _write(root, tmpl_rel,
               '\n'.join(f'### {h}' for h in headings) + '\n')
    # v0.3 templates — they also need evidence column sub-tables
    # (Touchpoint type / Exit code / Conflict markers) to satisfy
    # validate_v0_3_evidence_columns.
    for tmpl_rel, headings in [
        ('templates/implementation-control-log.v0.3.md',
         validate.REQUIRED_V03_TEMPLATE_HEADINGS),
        ('templates/implementation-control-log.zh-TW.v0.3.md',
         validate.REQUIRED_V03_ZH_TW_TEMPLATE_HEADINGS),
        ('docs/automation/evidence-layer-v0.3.md',
         validate.REQUIRED_V03_EVIDENCE_LAYER_HEADINGS),
    ]:
        # Build a v0.3 template stub: headings + an evidence block that
        # includes the v0.3-mandatory columns.
        body_lines = [f'### {h}' for h in headings]
        body_lines += [
            '',
            '### 9.5.6 stub',
            '',
            '| Path | Touchpoint type | Why this is high-risk |',
            '|---|---|---|',
            '| sample.ts | payment | example |',
            '',
            '### 9.5.7 stub',
            '',
            '| Rollback step | Command | Exit code | Conflict markers | Verified by |',
            '|---|---|---:|---|---|',
            '| Revert commit | `git revert HEAD` | 0 | 0 unmerged, 0 .rej | n/a |',
        ]
        _write(root, tmpl_rel, '\n'.join(body_lines) + '\n')
    # v0.3.1 templates — heading schema same as v0.3, plus the 0.5
    # block. Examples must pass the FULL 0.5 gate, so the example
    # stub also fills all 0.5 rows.
    for tmpl_rel, headings in [
        ('templates/implementation-control-log.v0.3.1.md',
         validate.REQUIRED_V03_1_TEMPLATE_HEADINGS),
        ('templates/implementation-control-log.zh-TW.v0.3.1.md',
         validate.REQUIRED_V03_1_ZH_TW_TEMPLATE_HEADINGS),
        ('docs/automation/evidence-layer-v0.3.1.md',
         validate.REQUIRED_V03_1_EVIDENCE_LAYER_HEADINGS),
    ]:
        # Build a v0.3.1 template stub with the 9.5.6 / 9.5.7 column
        # gate satisfied. The 0.5 block is left empty in templates —
        # only the example is gated for 0.5 row completeness.
        body_lines = [f'### {h}' for h in headings]
        body_lines += [
            '',
            '### 9.5.6 stub',
            '',
            '| Path | Touchpoint type | Why this is high-risk |',
            '|---|---|---|',
            '| sample.ts | payment | example |',
            '',
            '### 9.5.7 stub',
            '',
            '| Rollback step | Command | Exit code | Conflict markers | Verified by |',
            '|---|---|---:|---|---|',
            '| Revert commit | `git revert HEAD` | 0 | 0 unmerged, 0 .rej | n/a |',
        ]
        _write(root, tmpl_rel, '\n'.join(body_lines) + '\n')
    # v0.3.1 example: must pass the FULL 0.5 gate. Build a stub
    # that fills 0.5 completely and has a high-risk 9.5.6 row with
    # a non-self approver, so the gate passes.
    v03_1_example_body = (
        '## 0.5 Actor & Provenance (v0.3.1 — required)\n'
        '\n'
        '| Field | Value |\n'
        '|---|---|\n'
        '| Agent model       | test-agent |\n'
        '| Agent session     | test-session |\n'
        '| Human approver    | @test-user |\n'
        '| Approval evidence | https://example.com/pr/1 |\n'
        '| Wall clock start  | 2026-01-01T00:00:00Z |\n'
        '| Wall clock end    | 2026-01-01T00:01:00Z |\n'
        '\n'
        '## 9.5.6 High-Risk Touchpoints (v0.3.1)\n'
        '\n'
        '| Path | Touchpoint type | Why this is high-risk |\n'
        '|---|---|---|\n'
        '| src/billing/x.ts | payment | example |\n'
        '\n'
        '## 9.5.7 Rollback Evidence (v0.3.1)\n'
        '\n'
        '| Rollback step | Command | Exit code | Conflict markers | Verified by |\n'
        '|---|---|---:|---|---|\n'
        '| Revert | `git revert HEAD` | 0 | 0 unmerged, 0 .rej | n/a |\n'
    )
    _write(root, 'examples/billing-change-control-log.v0.3.1.md',
           v03_1_example_body)

    # v0.5 task-level control log templates and design note.
    for tmpl_rel in [
        'templates/task-control-log.zh-TW.md',
        'templates/task-control-log.en.md',
        'examples/task-control-log-agent-install-v0.5.zh-TW.md',
    ]:
        _write(root, tmpl_rel,
               '\n'.join(f'## {h}' for h in validate.REQUIRED_TASK_CONTROL_LOG_HEADINGS) + '\n')
    _write(root, 'docs/automation/task-level-control-log-v0.5.md',
           '\n'.join(f'## {h}' for h in validate.REQUIRED_V05_DOC_HEADINGS) + '\n')


def test_validate_minimal_repo_passes(tmp_path):
    _minimal_repo(tmp_path)
    errors = validate.validate_repository(tmp_path, mode='repo')
    assert errors == [], f"unexpected errors: {errors}"


def test_validate_minimal_kit_passes(tmp_path):
    _minimal_repo(tmp_path)
    errors = validate.validate_repository(tmp_path, mode='kit')
    assert errors == [], f"unexpected errors: {errors}"


def test_validate_missing_required_file(tmp_path):
    _minimal_repo(tmp_path)
    (tmp_path / 'README.md').unlink()
    errors = validate.validate_repository(tmp_path, mode='repo')
    assert any('missing: README.md' == e for e in errors), errors


def test_validate_empty_required_file(tmp_path):
    _minimal_repo(tmp_path)
    (tmp_path / 'README.md').write_text('   \n', encoding='utf-8')
    errors = validate.validate_repository(tmp_path, mode='repo')
    assert any('empty: README.md' == e for e in errors), errors


def test_validate_skill_missing_frontmatter(tmp_path):
    _minimal_repo(tmp_path)
    _write(tmp_path, 'skills/ai-development-control-log/SKILL.md',
           'no frontmatter here\n')
    errors = validate.validate_repository(tmp_path, mode='repo')
    assert any('SKILL.md must start with frontmatter' == e for e in errors), \
        errors


def test_validate_skill_unclosed_frontmatter(tmp_path):
    _minimal_repo(tmp_path)
    _write(tmp_path, 'skills/ai-development-control-log/SKILL.md',
           "---\nname: foo\n")
    errors = validate.validate_repository(tmp_path, mode='repo')
    assert any('frontmatter must close' in e for e in errors), errors


def test_validate_skill_missing_field(tmp_path):
    _minimal_repo(tmp_path)
    _write(tmp_path, 'skills/ai-development-control-log/SKILL.md',
           "---\nname: foo\ndescription: bar\nlicense: MIT\n---\nbody\n")
    errors = validate.validate_repository(tmp_path, mode='repo')
    assert any('version:' in e for e in errors), errors


def test_validate_skill_empty_field(tmp_path):
    _minimal_repo(tmp_path)
    _write(tmp_path, 'skills/ai-development-control-log/SKILL.md',
           "---\nname:\ndescription: bar\nversion: 0.1\n"
           "license: MIT\n---\nbody\n")
    errors = validate.validate_repository(tmp_path, mode='repo')
    assert any('missing value for name:' in e for e in errors), errors


def test_validate_template_missing_section(tmp_path):
    _minimal_repo(tmp_path)
    _write(tmp_path, 'templates/implementation-control-log.md',
           '## Task Goal\n\n## AI-Made Decisions\n')
    errors = validate.validate_repository(tmp_path, mode='repo')
    assert any('template missing section: Verification Results' == e
               for e in errors), errors


def test_validate_zh_tw_template_missing_section(tmp_path):
    _minimal_repo(tmp_path)
    _write(tmp_path, 'templates/implementation-control-log.zh-TW.md',
           '## 任務目標\n## 使用者明確要求\n')
    errors = validate.validate_repository(tmp_path, mode='repo')
    assert any('zh-TW template missing section' in e for e in errors), errors


def test_validate_daily_digest_missing_section(tmp_path):
    _minimal_repo(tmp_path)
    # v0.4: include all 9 daily digest headings (1 minute summary
    # + 7 questions + 1 feedback) so the fixture is minimal-but-valid.
    # We then delete one and confirm the validator catches it.
    _write(tmp_path, 'templates/daily-decision-digest.zh-TW.md',
           '## 語言與讀者設定\n'
           '## AI 做了什麼？\n'
           '## 哪些是你明確要求的？\n'
           '## 哪些是 AI 自己決定的？\n'
           '## 偏離原本規格了嗎？\n'
           '## 有沒有碰到高風險操作？\n'
           '## 驗證了什麼？沒驗證什麼？\n'
           '## 出事怎麼退？\n'
           )
    errors = validate.validate_repository(tmp_path, mode='repo')
    assert any('daily digest missing section' in e and '你看得懂嗎' in e
               for e in errors), errors


def test_validate_delivery_automation_missing_section(tmp_path):
    _minimal_repo(tmp_path)
    _write(tmp_path, 'docs/automation/optional-delivery-automation.md',
           '## 自動寄送是選配，不是預設\n## 寄送通道\n')
    errors = validate.validate_repository(tmp_path, mode='repo')
    assert any('delivery automation missing section' in e
               for e in errors), errors


def test_validate_task_control_log_missing_section(tmp_path):
    _minimal_repo(tmp_path)
    headings = [h for h in validate.REQUIRED_TASK_CONTROL_LOG_HEADINGS
                if h != 'AI self-decided']
    _write(tmp_path, 'templates/task-control-log.en.md',
           '\n'.join(f'## {h}' for h in headings) + '\n')

    errors = validate.validate_repository(tmp_path, mode='repo')

    assert any('task control log missing section' in e and 'AI self-decided' in e
               for e in errors), errors


def test_validate_v05_doc_missing_section(tmp_path):
    _minimal_repo(tmp_path)
    _write(tmp_path, 'docs/automation/task-level-control-log-v0.5.md',
           '## Why v0.5\n## What changes in v0.5\n')

    errors = validate.validate_repository(tmp_path, mode='repo')

    assert any('v0.5 doc missing section' in e and 'What v0.5 does NOT do' in e
               for e in errors), errors


def test_validate_v02_template_missing_section(tmp_path):
    _minimal_repo(tmp_path)
    # Build a v0.2 template with 9.5.1 / 9.5.2 / 9.5.3 missing.
    headings = [h for h in validate.REQUIRED_V02_TEMPLATE_HEADINGS
                if h not in {'9.5.1 Changed Files',
                             '9.5.2 Diff Summary',
                             '9.5.3 Test Result'}]
    _write(tmp_path, 'templates/implementation-control-log.v0.2.md',
           '\n'.join(f'### {h}' for h in headings) + '\n')
    errors = validate.validate_repository(tmp_path, mode='repo')
    assert any('v0.2 template missing section: 9.5.1 Changed Files' == e
               for e in errors), errors
    assert any('v0.2 template missing section: 9.5.3 Test Result' == e
               for e in errors), errors


def test_validate_v02_zh_tw_template_missing_section(tmp_path):
    _minimal_repo(tmp_path)
    headings = [h for h in validate.REQUIRED_V02_ZH_TW_TEMPLATE_HEADINGS
                if h not in {'9.5.1 改動檔案', '9.5.2 Diff 摘要',
                             '9.5.3 測試結果'}]
    _write(tmp_path, 'templates/implementation-control-log.zh-TW.v0.2.md',
           '\n'.join(f'### {h}' for h in headings) + '\n')
    errors = validate.validate_repository(tmp_path, mode='repo')
    assert any('v0.2 zh-TW template missing section: 9.5.1 改動檔案' == e
               for e in errors), errors


def test_validate_evidence_layer_doc_missing_section(tmp_path):
    _minimal_repo(tmp_path)
    _write(tmp_path, 'docs/automation/evidence-layer-v0.2.md',
           '## Why v0.2\n## What changes in v0.2\n')
    errors = validate.validate_repository(tmp_path, mode='repo')
    assert any('evidence-layer doc missing section' in e for e in errors), \
        errors


# ---------------------------------------------------------------------------
# End-to-end: the real repo must still validate
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_real_repo_passes_repo_mode():
    errors = validate.validate_repository(REPO_ROOT, mode='repo')
    assert errors == [], f"real repo failed: {errors}"


def test_real_repo_passes_kit_mode():
    errors = validate.validate_repository(REPO_ROOT, mode='kit')
    assert errors == [], f"real repo failed: {errors}"


def test_real_repo_passes_strict_mode():
    errors = validate.validate_repository(REPO_ROOT, mode='strict')
    assert errors == [], f"real repo failed: {errors}"
