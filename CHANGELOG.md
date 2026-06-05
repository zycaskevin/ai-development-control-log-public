# Changelog

All notable changes to the AI Development Control Log are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

> Releases are auto-drafted by
> [release-drafter](https://github.com/release-drafter/release-drafter)
> on every push to `main`. The first manually-released version was v0.2.0;
> future versions will be published via the GitHub Actions workflow.

## [Unreleased]

### Added
- v0.5 task-level control logs: `templates/task-control-log.zh-TW.md`,
  `templates/task-control-log.en.md`, and
  `examples/task-control-log-agent-install-v0.5.zh-TW.md`.
- `scripts/collect_task_logs.py` parses same-day task logs so the daily
  digest can distinguish explicit user requests from AI self-decisions when
  evidence exists.
- Task-log parsing defensively redacts raw webhook URLs, tokens, API keys,
  passwords, and authorization values before they can appear in digest
  artifacts or delivery messages.
- `scripts/build_daily_digest.py --task-log-dir` now aggregates task logs
  for the digest date before falling back to the v0.4 git-only conservative
  language.
- `docs/automation/task-level-control-log-v0.5.md` and
  `docs/plans/v0.5-task-level-control-log-plan.md` document the v0.5
  evidence model, migration path, and acceptance criteria.

### Changed
- README files now explain the v0.5 task-log evidence path and clarify
  that the default daily digest still uses zero LLM tokens.
- Repo validator now gates v0.5 task-log templates, example, parser, and
  design note.

## [0.4.1] — 2026-06-05

### Security
- Sanitized daily digest delivery failures so malformed webhook URLs,
  Telegram bot tokens, Resend API keys, and raw network exceptions cannot
  leak secret values into GitHub Actions logs.
- Added regression tests for malformed Slack / Telegram / Resend delivery
  configuration and network exceptions.

### Fixed
- Aligned `validate_daily_digest.py` section-content extraction with its
  accepted heading matcher so `Section N.` headings are not falsely treated
  as empty.
- Added English and Simplified Chinese agent-assisted install task cards
  and copyable prompts.
- Expanded install docs with provider credential guidance, exact
  `gh variable set` / `gh secret set --body-file -` commands, artifact
  verification commands, rollback steps, and secret-rotation guidance.
- Updated README repo trees, workflow comments, and v0.4 design notes so
  they reference the full multilingual install flow.

## [0.4.0] — 2026-06-05

> v0.4 turns the Daily AI Decision Digest from a "template only" kit
> into something a non-engineering user can actually run and receive.
> It now ships a real daily GitHub Actions workflow, a readable git-based
> digest generator, opt-in delivery for Slack / Feishu / Telegram /
> Resend email, an agent-assisted install task card, and a rule-based
> validator that enforces the 7-question structure.

### What v0.4 changes
- `templates/daily-decision-digest.zh-TW.md` — rewritten. Adds:
  - **`## 📋 0. 1 分鐘版（給老闆看）`** as the first section.
  - **7 mandatory question sections** (Q1–Q7) explicitly mapped to
    the user's original 7 questions (AI did what / user asked / AI
    decided / deviated / high risk / verified / rollback).
  - **§8 Feedback** at the end, asking the reader to reply with
    ✅ / ⚠️ / ❌.
  - **Per-row credibility labels** on every claim.
  - **Empty-is-empty rule**: required sections must have real content.
- `templates/daily-decision-digest.en.md` — English version of the
  same structure.
- `examples/daily-decision-digest.zh-TW.md` — rewritten as a fully
  filled example showing what a real day's digest looks like.
- `scripts/validate_daily_digest.py` (new) — rule-based validator
  with unit tests. Enforces the 7-question structure and refuses
  to mark a digest complete if any question is unanswered or
  contains only the template placeholder.
- `scripts/build_daily_digest.py` (new) — builds a readable zh-TW
  daily digest from the last 24 hours of git activity, so the default
  workflow no longer uploads an empty scaffold.
- `scripts/send_daily_digest.py` (new) — opt-in external delivery for
  Slack, Feishu / Lark, Telegram, and Resend email. Defaults to `none`.
- `docs/install/agent-assisted-install.zh-TW.md` +
  `templates/agent-install-prompt.zh-TW.md` (new) — lets a user hand
  installation to a coding agent instead of learning GitHub Actions.
- `scripts/validate.py` — extended to also require the 9 daily-digest
  headings (per language) and the new validator / builder / sender /
  install files.
- `.github/workflows/daily-digest.yml` (new) — first workflow that
  actually builds a readable digest end-to-end. Schedule 02:00 UTC
  daily. External delivery is controlled by `DELIVERY_PROVIDER`.
- `docs/automation/daily-digest-v0.4.md` (new) — design note.
- `tests/test_validate_daily_digest.py` (new) — unit tests.
- `tests/test_validate.py` — fixture updated for new daily-digest
  heading requirements.
- `README.md` / `README.en.md` / `README.zh-CN.md` — "Does it write
  or send daily logs automatically?" section rewritten; adds
  "5-minute setup guide" and "Why is external send off by default?"
  explanation.

### Why v0.4

The shipped v0.3.1 daily digest examples were annotated
`# Example only: enable intentionally`, which forced every fork
author to re-implement the same glue. Even when digests did get
written, they failed the "can the user read this?" test. v0.4 closes
both gaps.

### What v0.4 does NOT do
- It does not call out to an LLM. The validator is rule-based.
- It does not send to Slack / email / Telegram by default. The user
  must opt in.
- It does not sign the digest or store it append-only. That is
  v0.3.1 territory.
- It does not collect feedback automatically. The §8 section asks
  for a reply; the user must file an issue or send a chat message.

### Migration from v0.3.1 → v0.4
- Stop using the v0.3.1 digest output as a user-facing report. It
  answers different questions than v0.4.
- Switch the workflow template reference from
  `examples/github-actions-daily-digest.yml` to
  `.github/workflows/daily-digest.yml`.
- Re-train your readers: v0.3.1 readers expected a work-log; v0.4
  readers should expect a 7-question authority report.

## [0.3.1] — 2026-06-04

> v0.3.1 turns the Evidence Layer from "Replit-proof" into
> "Replit-proof with a named human approver". The v0.3 gate
> catches the agent lying about scope (9.5.6) and rollback
> (9.5.7). The v0.3.1 gate catches the agent lying about
> approval: when 9.5.6 has a high-risk row, the gate refuses
> to validate a log whose 0.5 lists `Human approver:
> self-approved`.

### Added — Actor & Provenance (v0.3.1)
- `templates/implementation-control-log.v0.3.1.md` +
  `.zh-TW.v0.3.1.md` — v0.3.1 English / 繁中 templates.
  Section 0.5 (Actor & Provenance) is now hard required.
- `examples/billing-change-control-log.v0.3.1.md` — billing
  example with a complete 0.5 block, demonstrating a
  `@maintainer` approver for a `payment` high-risk row.
- `docs/automation/evidence-layer-v0.3.1.md` — design note.
- `scripts/collect_actor_metadata.py` — autofills the
  agent-side rows of 0.5 (Agent model, Agent session, Wall
  clock) from `HERMES_AGENT_MODEL` / `HERMES_AGENT_SESSION`
  / `HERMES_TASK_ID`. Leaves the human-side rows (Human
  approver, Approval evidence) blank for the human reviewer.

### Added — Tests and CI
- `tests/test_actor_metadata.py` — 22 unit tests covering
  the actor-metadata script (env, JSON mode, file output,
  zh-TW rendering) and the `validate_v0_3_1_actor_metadata`
  gate (missing 0.5, empty agent rows, blank-but-allowed
  human rows, self-approval with high-risk, no-high-risk
  self-approval pass, db-schema high-risk, wall clock
  ordering, invalid ISO-8601, 0.5 prefix matching with
  ampersand).
- `tests/test_validate.py` — extended `test_validate_*` to
  cover the v0.3.1 templates and the example that must
  pass the FULL 0.5 gate.
- `.github/workflows/validate.yml` — script smoke step now
  also runs `collect_actor_metadata.py` (markdown + JSON
  modes) and greps for the autofilled agent model.

### Changed
- `scripts/validate.py` — adds v0.3.1 templates / example /
  script / design doc to the REQUIRED file set. New gate
  `validate_v0_3_1_actor_metadata` enforces 0.5 row
  completeness and the self-approval rule. Templates may
  have empty 0.5 rows (placeholders); examples and any
  user log must pass the full gate.
- `scripts/validate.py` — `has_markdown_heading` regex
  widened to support `(...)` tails containing `&` (for
  `0.5 Actor & Provenance (...)`) and to allow numbering
  prefixes like `0.5` (no trailing dot) in addition to
  `0.5.`.

### Fixed
- `scripts/validate.py` — the previous `_table_first_col_to_second`
  helper looked for a header line containing the field
  name, which silently failed when the field name appeared
  only in a data row (the actual Section 0.5 layout). The
  helper was replaced with `_all_field_value_rows`, which
  walks every pipe table in the section and collects
  `{first_col: second_col}`.
- `scripts/validate.py` — the 9.5.6 self-approval check
  used a case-sensitive substring match that missed
  `Touchpoint type` when the field name was lowercased
  for comparison. The check now compares both sides in
  lowercase.
- `scripts/collect_actor_metadata.py` — initial draft of
  the task-id slicing rule (`task_id[:8]`) lost the
  human-meaningful tail of long task ids. The slice now
  keeps the last 8 characters, so `feat-12345678` ends
  with `-345678`, preserving the chronological signal of
  the task id while keeping the suffix short.

## [0.3.0] — 2026-06-04

> v0.3 turns the Evidence Layer from "cross-checkable" into
> "Replit-proof": the agent can no longer self-report scope
> (9.5.6) or hand-wave rollback (9.5.7). Both are now produced
> by the working tree and by `git`, not by the agent.

### Added — Replit-proof Evidence Layer (v0.3)
- `templates/implementation-control-log.v0.3.md` + `.zh-TW.v0.3.md` —
  v0.3 English / 繁中 templates. 9.5.6 now auto-detected, 9.5.7 now
  exercises a real `git revert`. Adds Section 0.5 (Actor & Provenance)
  as a v0.3.0 placeholder that becomes hard-required in v0.3.1.
- `scripts/collect_rollback_evidence.py` — runs
  `git revert --no-commit` on a throwaway worktree, captures
  exit code, conflict markers, and `.rej` / `.orig` sidecars,
  and emits a 9.5.7 markdown snippet. Read-only with respect
  to the user's branch.
- `scripts/detect_high_risk_touchpoints.py` — scans the working
  tree + staged changes against `config/high_risk_patterns.yml`
  and emits a 9.5.6 markdown snippet.
- `config/high_risk_patterns.yml` — seven categories of
  high-risk touchpoints (db-schema, payment, auth, secret,
  production-config, core-calculation, external-side-effect)
  with glob patterns and an `exempt_paths` allowlist.
- `examples/billing-change-control-log.v0.3.md` — billing example
  with the v0.3 Replit-proof sections, filled from real
  script runs against a fixture repo.
- `docs/automation/evidence-layer-v0.3.md` — design note: why
  Replit triggered v0.3, what v0.3 does / does not do.

### Added — Tests and CI
- `tests/test_collect_rollback_evidence.py` — 9 unit tests with
  real git fixture repos: clean / conflict / invalid SHA /
  worktree cleanup, plus render and `main()` in markdown + JSON
  modes.
- `tests/test_detect_high_risk_touchpoints.py` — 16 unit tests
  with real git fixture repos: pattern matching, glob-to-regex
  semantics, exempt paths, fallback to HEAD~1 when base == HEAD,
  render, and `main()` for five real-world shapes (Node billing,
  Prisma migration, Auth0 update, env change, webhook change).
- `tests/test_validate.py` — extended `test_validate_*` to cover
  v0.3 templates + the new `validate_v0_3_evidence_columns` gate.

### Added — Repo automation
- `validate_v0_3_evidence_columns` in `scripts/validate.py` —
  refuses to pass a v0.3 log whose 9.5.6 / 9.5.7 tables are
  missing the mandatory columns (Touchpoint type, Exit code,
  Conflict markers).

### Changed
- `scripts/validate.py` — adds v0.3 templates, the v0.3
  evidence-layer design doc, and the two new scripts to the
  REQUIRED file set.

### Fixed
- `scripts/collect_rollback_evidence.py` — initial implementation
  used `git revert --no-commit <sha>` inside a worktree checked
  out at `<sha>~1`, which only tested the trivial case. The
  updated implementation checks out the current branch tip and
  reverts `<sha>` against it, so the dry-run mirrors what a
  deployer would actually do in production.
- `scripts/detect_high_risk_touchpoints.py` — initial
  implementation used `fnmatch.fnmatch` for glob matching, which
  silently missed paths like `tests/billing/test_invoice.py`
  against `**/tests/**`. Replaced with a hand-rolled
  gitignore-style glob-to-regex that handles `**` correctly.
- `scripts/detect_high_risk_touchpoints.py` — when the user
  commits directly on `main` (so `main` and HEAD are the same
  ref), `main..HEAD` is empty and no touchpoints are detected.
  Now falls back to `HEAD~1..HEAD` so the user still gets
  useful output.

## [0.2.0] — 2026-06-04

### Added — Evidence Layer (v0.2)
- `templates/implementation-control-log.v0.2.md` — v0.2 English template
  with Section 9.5 (Evidence Layer), 7 sub-blocks:
  - 9.5.1 Changed Files (objective, anchored to `git diff`)
  - 9.5.2 Diff Summary per file
  - 9.5.3 Test Result (raw output, not "it passed")
  - 9.5.4 Verification Type (mock / unit / integration /
    live smoke / production)
  - 9.5.5 Commit Hash / PR Link
  - 9.5.6 High-Risk Touchpoints
  - 9.5.7 Rollback Evidence (actually-exercised rollback, not
    "revertible")
- `templates/implementation-control-log.zh-TW.v0.2.md` — same in 繁體中文
- `examples/billing-change-control-log.v0.2.md` — billing example with
  full Evidence Layer
- `docs/automation/evidence-layer-v0.2.md` — design note: why / what /
  how / what v0.2 does NOT do
- `scripts/collect_evidence.py` + `collect_evidence.sh` — auto-fills
  9.5.1 and 9.5.3 from `git diff` + a test runner

### Added — Tests and CI
- `tests/test_validate.py` — 30+ unit tests covering heading parsing,
  `frontmatter_value`, mode dispatch, end-to-end `validate_repository`
  against a `tmp_path` fixture, and real-repo passes in
  repo / kit / strict modes
- `tests/test_collect_evidence.py` — 20 unit tests with a real git
  fixture repo covering diff collection, render, test-command
  detection, run / pass / fail / skip / timeout, and `main()` in
  markdown and JSON modes
- `tests/conftest.py` — makes `scripts/` importable for pytest
- `.github/workflows/validate.yml` — switched from
  `unittest discover` to `pytest`. Added a 'Run script smoke' step
  that asserts `collect_evidence.py` produces the expected sections
  and valid JSON

### Added — Repo automation
- `.github/workflows/release-drafter.yml` — auto-drafts the next
  release notes from merged PRs
- `.github/release-drafter.yml` — release-drafter config: version
  bump rules, category labels, changelog template

### Changed
- `scripts/validate.py` — `has_markdown_heading` now allows
  optional numbering prefix (e.g. `9.5.1`) and tail (e.g.
  `9.5.5 Commit Hash / PR Link`) without loosening word-boundary
  semantics
- `scripts/validate.py` — enforces the 7 v0.2 sub-blocks in both
  English and 繁中 templates
- `README.md` — section 5 introduces the Evidence Layer, lists
  v0.2 files, updates the project tree
- `.github/workflows/validate.yml` — `actions/checkout` now uses
  `fetch-depth: 0` so `git diff main..HEAD` resolves in the
  collect_evidence smoke step

### Fixed
- `scripts/collect_evidence.py` — used `git diff main...HEAD`
  (three-dot / merge-base) which returns nothing when the current
  branch IS base, the most common case for an agent finishing a
  feature. Switched to `main..HEAD` (two-dot).
- `scripts/collect_evidence.py` — `--test-cmd "pytest -v tests/x.py"`
  was passed as a single argv element, so subprocess tried to exec
  a binary literally named `pytest -v tests/x.py` and failed with
  `command not found: p`. Now uses `shlex.split`.
- `scripts/collect_evidence.py` — exit code 127 (tool not installed)
  and 124 (timeout) were reported as `Fail`. They are now `Skip`,
  distinct from real `Fail`.
- `.github/workflows/validate.yml` — the old `unittest discover`
  step silently ran nothing on pytest-style `def test_*` functions,
  so all v0.1 tests had been unverified by CI.

## [0.1.x] — pre-2026-06-04

The v0.1 line established the original Implementation Control Log
(verifiable / partially / unverified credibility labels, mock / unit /
integration / live smoke / production test type labels, surgical
change traceability, high-risk / irreversible operation check,
daily decision digest, optional delivery automation).

See the [README](README.md) for the full history and the
[release archive](https://github.com/zycaskevin/ai-development-control-log/releases)
for prior versions.

[Unreleased]: https://github.com/zycaskevin/ai-development-control-log/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/zycaskevin/ai-development-control-log/compare/40425cb...v0.2.0
[0.1.x]: https://github.com/zycaskevin/ai-development-control-log/releases?after=40425cb
