# Evidence Layer — v0.2 Design Note

> v0.2 turns the AI Development Control Log from an AI self-report into
> a cross-checkable audit record. This file explains why and how.

## Why v0.2

v0.1 of the Control Log already separates:
- Report Credibility (verified / partially / unverified)
- Test Type Labels (mock / unit / integration / live smoke / production verified)
- Verified / Not Verified sections

But the same party — the AI agent — is the one writing the log.
That is the "watched is also the reporter" problem called out in 2026
by industry sources such as the Cloud Security Alliance's
*AI Agent Disclosure Vacuum* white paper: self-disclosure is not evidence.

The repo's own CLAUDE.md says: "if you can't verify it, you can't claim it."
v0.2 operationalizes that rule.

## What changes in v0.2

Added one new section in the template (9.5) with seven sub-blocks:

| Sub-block | What it anchors | Source of truth |
|---|---|---|
| 9.5.1 Changed Files | "What did the AI actually change?" | `git diff --name-status` |
| 9.5.2 Diff Summary (per file) | "What does each change do?" | `git diff` + human summary |
| 9.5.3 Test Result | "Did tests actually run?" | raw CI / pytest / vitest output |
| 9.5.4 Verification Type | "How strong is the evidence?" | one of mock / unit / integration / live smoke / production |
| 9.5.5 Commit Hash / PR Link | "Where can a human re-run this?" | git + PR URL |
| 9.5.6 High-Risk Touchpoints | "Did AI cross a sensitive boundary?" | path + touchpoint type |
| 9.5.7 Rollback Evidence | "Was the rollback path actually exercised?" | dry-run / backup / tag |

A new companion script (`scripts/collect_evidence.py`) generates 9.5.1 and
9.5.3 directly from the working tree so the AI does not retype them by hand.

## How to use v0.2

For non-trivial tasks (see CLAUDE.md for the definition), agents should:

1. Open the v0.2 template: `templates/implementation-control-log.v0.2.md`
   (or `templates/implementation-control-log.zh-TW.v0.2.md` for zh-TW).
2. Run `python scripts/collect_evidence.py` to fill 9.5.1 and 9.5.3.
3. Hand-fill 9.5.2, 9.5.4, 9.5.6 by reading the diff.
4. For any change that touches a High-Risk Touchpoint, also fill 9.5.7
   with an actually-exercised rollback step, not a wish.

## What v0.2 does NOT do

- It does not replace human code review.
- It does not guarantee the AI told the truth.
  It only makes the truth cheaper to check.
- It does not block "I don't know" answers.
  If a section cannot be filled honestly, write `Unknown — see risk` and
  lower the Report Credibility in 9.1.

## Why this matters for the repo

- Honest answer to "the Log is AI self-reporting":
  the repo now provides objective artifacts, not just claims.
- Honest answer to "this is just AI Coding hype":
  the repo's value is not "AI wrote code". Its value is
  "AI's change is auditable, with evidence, before merge".
- Aligned with 2026 industry direction:
  - NIST AI RMF 1.0 — risk identification + management
  - EU AI Act 2026/08 — automatic logging for high-risk AI
  - CSA *AI Agent Disclosure Vacuum* 2026 —
    "self-disclosure is not evidence"
