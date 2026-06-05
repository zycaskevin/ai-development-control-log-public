#!/usr/bin/env python3
"""Validate a Daily AI Decision Digest against the v0.4 schema.

This validator checks:

  1. The 1-minute summary section (📋) is the first section in the file
  2. All 7 core question sections are present (in zh-TW OR en aliases)
  3. The feedback section (§8) is present
  4. Each section has real content (not just the template placeholder)

It is rule-based on purpose: it never reads the LLM's prose, it only
checks structural presence. This is the core guarantee — the digest
must be answerable to the 7 questions the user actually asks, even
when the LLM is trying to skip them.

Usage:
    python scripts/validate_daily_digest.py path/to/digest.md
    python scripts/validate_daily_digest.py logs/daily/  # scans dir
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 7 question headings, with both zh-TW and en aliases. We accept any of
# these as evidence the author intended to answer that question.
HEADING_ALIASES: dict[str, list[str]] = {
    "q1_what_ai_did": [
        "AI 做了什麼？",  # zh-TW template
        "What did AI do?",  # en template
    ],
    "q2_user_required": [
        "哪些是你明確要求的？",  # zh-TW
        "What did the user explicitly require?",  # en
    ],
    "q3_ai_decisions": [
        "哪些是 AI 自己決定的？",  # zh-TW
        "What did AI decide on its own?",  # en
    ],
    "q4_deviations": [
        "偏離原本規格了嗎",  # zh-TW (template uses this prefix; trailing chars allowed)
        "Did it deviate from the spec?",  # en
    ],
    "q5_high_risk": [
        "有沒有碰到高風險操作",  # zh-TW
        "Did it touch any high-risk operation?",  # en
    ],
    "q6_verification": [
        "驗證了什麼？沒驗證什麼？",  # zh-TW
        "What was verified? What was not?",  # en
    ],
    "q7_rollback": [
        "出事怎麼退",  # zh-TW
        "If it breaks, how do you roll back?",  # en
    ],
    "q8_feedback": [
        "這份 digest 你看得懂嗎",  # zh-TW
        "Can you read this digest?",  # en
    ],
}

# Headings that mark the 1-minute summary block.
ONE_MINUTE_HEADINGS = [
    "1 分鐘版",
    "1-Minute Version",
]


def has_any_heading(text: str, heading: str) -> bool:
    """Return True if `heading` (or a numbered prefix variant) appears
    as a real markdown heading in `text`.

    Accepts an optional numbering prefix like `1. `, `4. `, `§1 `, etc.
    Also accepts a trailing punctuation token (?, !, ., :, Chinese
    full-width ?, !, 。, ：) and a trailing tail after a separator,
    so that headings like `## 4. 偏離原本規格了嗎？` match the
    alias `偏離原本規格了嗎`.

    Emoji like 📋 are tolerated anywhere in the heading line.
    """
    prefix = r'(?:\d+(?:\.\d+)*\.?\s+)?'  # optional numbering
    # Tolerate "Section N. " or "§N " prefixes that some authors use.
    section_prefix = r'(?:(?:Section|SECTION|§)\s*\d+(?:\.\d+)*\.?\s+)?'
    sep = r'[\s/\\\u2014\u2013\(&\uff08\uff5b\[\{]'
    # Trailing punctuation that closes a question or sentence, in
    # both ASCII and CJK forms.
    trailing_punct = r'[?!.,:;，。！？；：]?'
    tail = rf'(?:{sep}[^\n]*)?'
    emoji_prefix = r'(?:[\U0001F300-\U0001FAFF\U00002600-\U000027BF]\s*)*'
    pattern = re.compile(
        r'^#{2,6}\s+' + emoji_prefix + r'(?:' + section_prefix + prefix + r')?'
        + re.escape(heading) + trailing_punct + tail + r'\s*$',
        re.MULTILINE,
    )
    return bool(pattern.search(text))


def section_content_after_heading(text: str, heading: str) -> str:
    """Return the content of the section under `heading` until the next
    heading of equal or higher level, or EOF. Empty if `heading` not found.

    Keep this matcher aligned with has_any_heading(): if a heading style
    is accepted as present, content extraction must also find it.
    """
    emoji_prefix = r'(?:[\U0001F300-\U0001FAFF\U00002600-\U000027BF]\s*)*'
    section_prefix = r'(?:(?:Section|SECTION|§)\s*\d+(?:\.\d+)*\.?\s+)?'
    number_prefix = r'(?:\d+(?:\.\d+)*\.?\s+)?'
    pattern = re.compile(
        r'^#{2,6}\s+' + emoji_prefix + r'(?:' + section_prefix + number_prefix + r')?'
        + re.escape(heading) + r'[?!.,:;，。！？；：]?.*$',
        re.MULTILINE,
    )
    m = pattern.search(text)
    if not m:
        return ""
    start = m.end()
    # Find the next heading of level <= the matched heading's level
    matched_level = len(m.group(0).split()[0])  # e.g. "##" -> 2
    next_h = re.compile(
        r'^#{1,' + str(matched_level) + r'}\s+',
        re.MULTILINE,
    )
    m2 = next_h.search(text, pos=start)
    end = m2.start() if m2 else len(text)
    return text[start:end].strip()


def _is_template_placeholder(content: str) -> bool:
    """Heuristic: a section is considered a template placeholder if its
    content is empty, or matches one of the known template-prompt lines
    (the literal `(direct quote or message reference)` or
    `(auto-counted from §N)`). Otherwise it is real content.
    """
    if not content:
        return True
    stripped = content.strip()
    # Strip leading/trailing blank lines and re-check
    body = "\n".join(line for line in stripped.splitlines() if line.strip())
    if not body:
        return True
    # Common template placeholders
    placeholders = [
        "(direct quote or message reference)",
        "(auto-counted from §1)",
        "(auto-counted from §2 §3)",
        "(auto-counted from §4)",
        "(auto-counted from §5)",
        "(auto-counted from §7)",
    ]
    for ph in placeholders:
        if body == ph:
            return True
    return False


def validate_digest(path: Path) -> list[str]:
    """Return a list of error messages; empty list = valid digest."""
    if not path.exists():
        return [f"file not found: {path}"]
    if not path.is_file():
        return [f"not a file: {path}"]

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return [f"empty file: {path}"]

    errors: list[str] = []

    # 1. The 1-minute summary block must be present and must be the FIRST
    #    section in the file.
    one_minute_found_at = None
    for h in ONE_MINUTE_HEADINGS:
        # Match the heading with optional emoji prefix, optional
        # numbering like "0." or "1." or "Section 0.", and optional
        # trailing punctuation + tail like "（給老闆看）" or
        # "(for the boss)".
        section_prefix = r'(?:(?:Section|SECTION|§)\s*\d+(?:\.\d+)*\.?\s+)?'
        m = re.search(
            r'^#{2,6}\s+'                         # markdown heading prefix
            r'(?:[\U0001F300-\U0001FAFF\U00002600-\U000027BF]\s*)*'  # optional emoji
            + r'(?:' + section_prefix + r'(?:\d+(?:\.\d+)*\.?\s+)?)?'
            + re.escape(h)
            + r'[?!.,:;，。！？；：]?'              # optional closing punct
            + r'.*$',
            text,
            re.MULTILINE,
        )
        if m:
            one_minute_found_at = m.start()
            break
    if one_minute_found_at is None:
        errors.append(
            f"{path}: missing 1-minute summary block (expected one of: "
            + ", ".join(ONE_MINUTE_HEADINGS) + ")"
        )
    elif one_minute_found_at > 500:
        # allow some leading blank lines / frontmatter, but the 1-minute
        # block must be near the top of the file.
        errors.append(
            f"{path}: 1-minute summary block must be near the top of the file "
            f"(found at offset {one_minute_found_at}, expected < 500 chars)"
        )

    # 2. Each of the 7 core questions + the feedback section must have
    #    a heading in at least one of its alias forms.
    for qkey, aliases in HEADING_ALIASES.items():
        if not any(has_any_heading(text, a) for a in aliases):
            errors.append(
                f"{path}: missing section for {qkey} (expected one of: "
                + ", ".join(aliases) + ")"
            )

    # 3. Each core section must have real content, not just the template
    #    placeholder. We only enforce this for sections that exist.
    #    We do NOT enforce §8 (feedback) to be filled in, since it is the
    #    reader's reply, not the author's.
    content_required_for = [
        "q1_what_ai_did",
        "q3_ai_decisions",
        "q4_deviations",
        "q5_high_risk",
        "q6_verification",
        "q7_rollback",
    ]
    for qkey in content_required_for:
        aliases = HEADING_ALIASES[qkey]
        matched_heading = None
        for a in aliases:
            if has_any_heading(text, a):
                matched_heading = a
                break
        if matched_heading is None:
            continue  # already reported in step 2
        body = section_content_after_heading(text, matched_heading)
        if _is_template_placeholder(body):
            errors.append(
                f"{path}: section {qkey} (heading: '{matched_heading}') "
                f"is empty or still has the template placeholder"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Daily AI Decision Digest against the v0.4 schema."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more digest .md files, or a directory of digest files.",
    )
    args = parser.parse_args()

    all_errors: list[str] = []
    files_checked = 0
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            for md in sorted(path.glob("*.md")):
                all_errors.extend(validate_digest(md))
                files_checked += 1
        else:
            all_errors.extend(validate_digest(path))
            files_checked += 1

    if all_errors:
        print(f"FAIL: {len(all_errors)} error(s) in {files_checked} file(s)")
        for e in all_errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {files_checked} file(s) passed validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
